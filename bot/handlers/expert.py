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
from messages import get_instructions
from logger import logger
from config import STAGES

expert_router = Router()


"""Обработчики сообщений эксперта."""


@expert_router.message(
        Labelling.waiting_expert_command, 
        F.text.in_(["Начать разметку", "Разметить следующий снимок"]) 
)
async def start_labelling(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение, если пользователь отправил 'Начать разметку'
    в состоянии ожидания команды эксперта.
    Подгружает пользователю снимок для разметки, если такой имеется.
    """
    logger.info(f"Начинаю обработку")
    data = await state.get_data()
    user_id = data["user_id"]
    user_status = data["user_status"]
    await state.set_state(Labelling.labelling)

    current_tooth_id, teeth_num = await rq.get_tooth_id(user_id, user_status)

    await state.update_data(tooth_id=current_tooth_id)
    await state.update_data(teeth_num=teeth_num)

    tooth_files, tooth_complexity = await rq.get_tooth(current_tooth_id)
    tooth_complexity_str = ""
    if tooth_complexity:
        tooth_complexity_str = "(сложный случай)"
    await state.update_data(tooth_complexity_str=tooth_complexity_str)    


    if not current_tooth_id: 
        await message.answer('Отсутствуют данные для разметки.')
        return
   
    if not tooth_files:
        await state.set_state(Labelling.waiting_expert_command)
        await message.answer('Отсутствуют данные для разметки.')
        return

    if current_tooth_id > teeth_num:
        await state.set_state(Labelling.waiting_expert_command)
        await message.answer('Вы разметили все снимки.')
        return
    
    
    await state.update_data(selected_id=0)
    await state.update_data(stage='conditions')
    await state.update_data(selected=[0, 0, 0, 0])
        
    photos = [
        InputMediaPhoto(media=FSInputFile(tooth_files[0])),
        InputMediaPhoto(media=FSInputFile(tooth_files[1]))
    ]
    await message.answer(text="Снимок для разметки подгружается...",
                        reply_markup=ReplyKeyboardRemove())
    await message.answer_media_group(media=photos)
    instruction = get_instructions('conditions')
    await message.answer(
        text=(
            f'Снимок {tooth_complexity_str} №{current_tooth_id} из {teeth_num}.\n'
            f'{instruction}'
        ),
        reply_markup=await kb.show_labels('conditions', 0)
    )


@expert_router.callback_query(
        Labelling.labelling, 
        F.data.startswith("label_")
)
async def select_labels(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Начинаю обработку")
    """
    Обрабатывает callback в состоянии ожидания класса разметки, 
    если callback_data начинается с 'label_'. 

    Если callback_data == 'label_confirm', то изменяет текст сообщения,
    добавляет InlineKeyboard для подтверждения выбранных классов разметки.

    Если callback_data == 'label_complex', то изменяет текст сообщения,
    добавляет InlineKeyboard для подтверждения сложного случая.

    Иначе изменяет InlineKeyboard в соответствии с выбранными классами разметки
    """
    data = await state.get_data()
    # selected_id = data["selected_id"]
    stage = data["stage"]
    stage_id = STAGES.index(data["stage"])
    selected = data['selected']

    action = callback.data.split('_')[1]

    if action == "confirm":
        await state.set_state(Labelling.confirming_label)
        selected_name = await rq.get_label_name(stage, selected[stage_id])
        caption = f"Подтвердите свой выбор: {selected_name}"  

        await callback.message.edit_text(
            text=caption,
            reply_markup=await kb.confirmation_keyboard('0')
        )
    elif action == "complex":
        await state.set_state(Labelling.confirming_label)
        caption = "Вы отметили, что сомневаетесь в ответе."

        selected[STAGES.index(data["stage"])] = 1
        await state.update_data(selected=selected)
        await callback.message.edit_text(
            text=caption,
            reply_markup=await kb.confirmation_keyboard('1')
        )
    else:
        label_id = callback.data.split('_')[1]
        if label_id == selected[stage_id]:
            selected[stage_id] = 0
        else:
            selected[stage_id] = label_id
        await state.update_data(selected=selected)
        await callback.message.edit_reply_markup(
            reply_markup=await kb.show_labels(stage, selected[stage_id])
        )


@expert_router.callback_query(Labelling.confirming_label,
                              F.data.startswith("confirm_"))
async def confirm_label(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Начинаю обработку")
    """
    Обрабатывает callback в состоянии подтверждения разметки, 
    если callback_data начинается с 'confirm_'

    Переходит на следующий этап разметки, если такой имеется.
    Иначе, сохраняет результат разметки.
    """
    await state.set_state(Labelling.labelling)
    data = await state.get_data()
    complexity = callback.data.split('_')[1]
    if complexity == '1':
        await rq.change_tooth_complexity(data['tooth_id'], True)

    current_stage_index = STAGES.index(data['stage'])
    if current_stage_index + 1 >= len(STAGES):

        user_id = data["user_id"]
        tooth_id = data["tooth_id"]
        selected = data["selected"]

        await rq.add_answer(
            tg_id=user_id,
            tooth_id=tooth_id,
            condition_id=selected[0],
            pathology_id=selected[1],
            rec_id=selected[2],
            term_id=selected[3]
        )

        await state.update_data(selected=[0, 0, 0, 0], stage='conditions')
        
        await callback.message.edit_reply_markup(reply_markup=None)
        await state.set_state(Labelling.waiting_expert_command)
        teeth_num = data["teeth_num"]
        progress = int(tooth_id / teeth_num * 10)
        bar = "█" * progress + "—" * (10 - progress)
        text = (
            f'Снимок {data["tooth_complexity_str"]} №{data["tooth_id"]} из '
            f'{teeth_num}.\n'
            f'Разметка успешно добавлена.\n'
            f'Размечено: [{bar}] {round((tooth_id / teeth_num) * 100)}%'
        )
        await callback.message.answer(
            text=text,
            reply_markup=kb.label_next
        )
    else:
        new_stage = STAGES[current_stage_index + 1]
        await state.update_data(stage=new_stage)

        await callback.message.edit_text(
            text=get_instructions(new_stage),
            reply_markup=await kb.show_labels(new_stage, 0)
        )


@expert_router.callback_query(Labelling.confirming_label,
                              F.data == "go_back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Начинаю обработку")
    """
    Обрабатывает callback в состоянии подтверждения класса разметки, 
    если callback_data == 'go_back'.
    Возвращает пользователя на этап выбора классов разметки. 
    """
    await state.set_state(Labelling.labelling)
    data = await state.get_data()
    stage_id = STAGES.index(data["stage"])
    selected = data['selected']
    selected[stage_id] = 0
    await state.update_data(selected=selected)

    instruction = get_instructions(data['stage'])
    text = (
        f'Снимок {data["tooth_complexity_str"]} №{data["tooth_id"]}.\n'
        f'{instruction}'
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=await kb.show_labels(data['stage'], 0)
    )


@expert_router.callback_query(Labelling.labelling, F.data == "end")
async def end_labelling(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Начинаю обработку")
    """
    Обрабатывает callback, если callback_data == 'end'.
    Возвращает эксперта на этап выбора команды. 
    """
    await state.set_state(Labelling.waiting_expert_command)
    await state.update_data(selected=[0, 0, 0, 0])
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text="Разметка завершена.")
    await callback.message.answer(
        text="Выберите команду.",
        reply_markup=kb.expert_commands
    )


@expert_router.message(Labelling.waiting_expert_command, 
                       F.text == "Завершить разметку")
async def end_labelling(message: Message, state: FSMContext):
    logger.info(f"Начинаю обработку")
    """
    Обрабатывает если callback_data == 'end'.
    Возвращает эксперта на этап выбора команды. 
    """
    await state.update_data(selected=[0, 0, 0, 0])
    await message.answer(text="Разметка завершена.")
    await message.answer(
        text="Выберите команду.",
        reply_markup=kb.expert_commands
    )