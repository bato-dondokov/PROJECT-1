from aiogram import F, Router
from aiogram.types import (
    Message, 
    FSInputFile, 
    CallbackQuery, 
    ReplyKeyboardRemove,
    InputMediaPhoto 
)
from aiogram.fsm.context import FSMContext

import keyboards.keyboards as kb
import database.requests as rq 
from states.labelling import Labelling
from messages import LABEL_INSTRUCTIONS, RECS_INSTRUCTIONS

expert_router = Router()


"""
Обработчики сообщений эксперта.
"""


@expert_router.message(
        Labelling.waiting_expert_command, 
        (F.text == "Начать разметку")
)
async def start_labelling(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение, если пользователь отправил 'Начать разметку'
    в состоянии ожидания команды эксперта.

    Подгружает пользователю снимок для разметки, если такой имеется.
    """
    user_id = message.from_user.id
    await state.update_data(user_id=user_id)
    await state.set_state(Labelling.waiting_label)

    current_tooth_id, teeth_num = await rq.get_user_current_tooth_id(user_id)
    await state.update_data(tooth_id=current_tooth_id)
    await state.update_data(teeth_num=teeth_num)

    tooth_files = await rq.get_tooth(current_tooth_id)

    if current_tooth_id > teeth_num:
        await state.set_state(Labelling.waiting_expert_command)
        await message.answer('Вы разметили все снимки.')
        return
    
    if not tooth_files:
        await state.set_state(Labelling.waiting_expert_command)
        await message.answer('Отсутствуют данные для разметки.')
        return
    
    await state.update_data(selected_labels={})
    photos = [
        InputMediaPhoto(media=FSInputFile(tooth_files[0])),
        InputMediaPhoto(media=FSInputFile(tooth_files[1]))
    ]

    await message.answer(text="Снимок для разметки подгружается...",
                        reply_markup=ReplyKeyboardRemove())
    await message.answer_media_group(media=photos)
    await message.answer(
        text=f'''Снимок №{current_tooth_id} из {teeth_num}.
        \n{LABEL_INSTRUCTIONS}''',
        reply_markup=await kb.show_labels({})
    )


@expert_router.callback_query(
        Labelling.waiting_label, 
        F.data.startswith("label_")
)
async def select_labels(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback в состоянии ожидания класса разметки, 
    если callback_data начинается с 'label_'. 

    Если callback_data == 'label_confirm', то изменяет текст сообщения,
    добавляет InlineKeyboard для подтверждения выбранных классов разметки.

    Иначе изменяет InlineKeyboard в соответствии с выбранными классами разметки
    """
    data = await state.get_data()
    selected_labels = data["selected_labels"]

    action = callback.data.split('_')[1]

    if action == "confirm":
        await state.set_state(Labelling.confirming_label)
        caption = "Подтвердите свой выбор:\n"+"\n".join(selected_labels.values())

        await callback.message.edit_text(
            text=caption,
            reply_markup=kb.confirming
        )
    else:
        label_id = callback.data.split('_')[1]
        label_name = callback.data.split('_')[2]
        if label_id in selected_labels:
            del selected_labels[label_id]
        else:
            selected_labels[label_id] = label_name
        await state.update_data(selected_labels=selected_labels)
        await callback.message.edit_reply_markup(
            reply_markup=await kb.show_labels(selected_labels)
        )
    

@expert_router.callback_query(Labelling.confirming_label, F.data == "confirm")
async def confirm_label(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback в состоянии подтверждения разметки.
    Изменяет состояние на ожидание рекомендаций к лечению.
    Изменяет текст и InlineKeyboard.
    """
    await state.update_data(selected_rec={'id':0, 'name':None})
    await state.set_state(Labelling.waiting_recommendation)
    await callback.message.edit_text(
        text=RECS_INSTRUCTIONS,
        reply_markup=await kb.recommendation_keyboard(0)
    )


@expert_router.callback_query(
        Labelling.waiting_recommendation, 
        F.data.startswith("rec_")
)
async def select_recommendation(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback в состоянии ожидания рекомендации к лечению, 
    если callback_data начинается с 'rec_'. 

    Если callback_data == 'rec_confirm', то изменяет текст сообщения,
    добавляет InlineKeyboard для подтверждения выбранной рекомендации.

    Иначе изменяет InlineKeyboard в соответствии с выбранной рекомендацией.
    """
    data = await state.get_data()
    selected_rec = data["selected_rec"]

    action = callback.data.split('_')[1]

    if action == "confirm":
        await state.set_state(Labelling.confirming_rec)
        caption = f"Подтвердите свой выбор: {selected_rec['name']}"

        await callback.message.edit_text(
            text=caption,
            reply_markup=kb.confirming
        )
    else:
        rec_id = callback.data.split('_')[1]
        rec_name = callback.data.split('_')[2]
        if rec_id == selected_rec['id']:
            selected_rec['id'] = 0
            selected_rec['name'] = None
        else:
            selected_rec['id'] = rec_id
            selected_rec['name'] = rec_name
        await state.update_data(selected_rec=selected_rec)
        await callback.message.edit_reply_markup(
            reply_markup=await kb.recommendation_keyboard(selected_rec['id'])
        )
 

@expert_router.callback_query(Labelling.confirming_rec, F.data == "confirm")
async def confirm_req(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback в состоянии подтверждения рекомендации к лечению.
    Добавляет данные о разметке в БД.
    Изменяет состояние на ожидание команды Эксперта.
    Отправляет сообщение об успешно размеченном снимке. 
    Добавляет InlineKeyboard команд Эксперта.
    """
    data = await state.get_data()
    user_id = data["user_id"]
    tooth_id = data["tooth_id"]
    selected_labels = data["selected_labels"].keys()
    label_ids = ", ".join(selected_labels)
    rec_id = data["selected_rec"]['id']

    await rq.add_answer(
        tg_id=user_id,
        tooth_id=tooth_id,
        label_ids=label_ids,
        rec_id=rec_id
    )

    new_tooth_id = int(tooth_id) + 1
    await state.update_data(
        selected_labels={},
        selected_rec={'id':0, 'name':None},
        tooth_id=new_tooth_id
    )
    await rq.set_user_current_tooth_id(
        tg_id=data["user_id"], 
        tooth_id=new_tooth_id
    )
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(Labelling.waiting_expert_command)
    teeth_num = data["teeth_num"]
    progress = int(tooth_id / teeth_num * 10)
    bar = "█" * progress + "—" * (10 - progress)
    await callback.message.answer(
        text=f'''Снимок №{data["tooth_id"]} из {teeth_num}.
        \nРазметка успешно добавлена.
        \nРазмечено: [{bar}] {round((tooth_id / teeth_num) * 100)}%''',
        reply_markup=kb.label_next
    )


@expert_router.callback_query(Labelling.confirming_label, F.data == "go_back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback в состоянии подтверждения класса разметки, 
    если callback_data == 'go_back'.
    Возвращает пользователя на этап выбора классов разметки. 
    """
    await state.set_state(Labelling.waiting_label)
    await state.update_data(selected_labels={})
    data = await state.get_data()

    await callback.message.edit_caption(
        caption=f'Снимок №{data["tooth_id"]}.\n{LABEL_INSTRUCTIONS}',
        reply_markup=await kb.show_labels({})
    )


@expert_router.callback_query(
        Labelling.waiting_expert_command,
        F.data == "end_labelling"
)
async def end_labelling(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback в состоянии ожидания команды эксперта, 
    если callback_data == 'end_labelling'.
    Возвращает эксперта на этап выбора команды. 
    """
    await state.set_state(Labelling.waiting_expert_command)
    await state.update_data(selected_labels={})
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text="Разметка завершена.")
    await callback.message.answer(
        text="Выберите команду.",
        reply_markup=kb.expert_commands
    )
    

@expert_router.callback_query(
        Labelling.waiting_expert_command, 
        F.data == "label_next"
)
async def label_next(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback в состоянии ожидания команды эксперта, 
    если callback_data == 'label_next'.
    Отправляет эксперту новый снимок для разметки. 
    """
    await state.set_state(Labelling.waiting_label)
    await state.update_data(selected_labels={})
    await callback.message.edit_reply_markup(reply_markup=None)
    
    data = await state.get_data()
    if data["tooth_id"] > data["teeth_num"]:
        await state.set_state(Labelling.waiting_expert_command)
        await callback.message.answer(text='Вы разметили все снимки.',
                                      reply_markup=kb.expert_commands)
        return

    tooth_files = await rq.get_tooth(data["tooth_id"])
    if not tooth_files:
        await state.set_state(Labelling.waiting_expert_command)
        await callback.message.answer(text='Отсутствуют данные для разметки.',
                                      reply_markup=kb.expert_commands)
        return

    photos = [
        InputMediaPhoto(media=FSInputFile(tooth_files[0])),
        InputMediaPhoto(media=FSInputFile(tooth_files[1]))
    ]
    await callback.message.answer(text="Снимок для разметки подгружается...",
                                  reply_markup=ReplyKeyboardRemove())
    await callback.message.answer_media_group(media=photos)
    await callback.message.answer(
        text=f'''Снимок №{data["tooth_id"]} из {data["teeth_num"]}.
        \n{LABEL_INSTRUCTIONS}''',
        reply_markup=await kb.show_labels({})
    )    