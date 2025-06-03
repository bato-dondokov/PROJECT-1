from aiogram import F, Router
from aiogram.types import (
    Message, 
    FSInputFile, 
    CallbackQuery, 
    ReplyKeyboardRemove
)
from aiogram.fsm.context import FSMContext

import keyboards.keyboards as kb
import database.requests as rq 
from states.labelling import Labelling

expert_router = Router()

LABEL_INSTRUCTIONS = (
    "Нажмите 1 раз, чтобы выбрать подходящий вариант разметки, "
    "2 раза — отменить выбор.\n"
    "Выбрать можно 1 или более вариантов.\n"
    "Для отправки разметки нажмите «Подтвердить»."
)

@expert_router.message(
        Labelling.waiting_expert_command, 
        (F.text == "Начать разметку") | (F.data == "label_next")
)
async def start_labelling(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(user_id=user_id)
    await state.set_state(Labelling.waiting_label)

    current_tooth_id = await rq.get_user_current_tooth_id(user_id)
    await state.update_data(tooth_id=current_tooth_id)

    tooth_file_path = await rq.get_tooth(current_tooth_id)

    if not tooth_file_path:
        await message.answer('Отуствуют данные для разметки.')
        return
    
    await state.update_data(selected={})
    photo = FSInputFile(tooth_file_path)

    await message.answer(text="Снимок для разметки подргужается...",
                        reply_markup=ReplyKeyboardRemove())
    
    await message.answer_photo(
        photo=photo,
        caption=f'Снимок №{current_tooth_id}.\n{LABEL_INSTRUCTIONS}',
        reply_markup=await kb.show_labels({})
    )


@expert_router.callback_query(
        Labelling.waiting_label, 
        F.data.startswith("label_")
)
async def select_labels(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data["selected"]

    action = callback.data.split('_')[1]

    if action == "confirm":
        await state.set_state(Labelling.confirming_label)
        caption = "Подтвердите свой выбор:\n" + "\n".join(selected.values())

        await callback.message.edit_caption(
            caption=caption,
            reply_markup=kb.confirming
        )
    else:
        label_id = callback.data.split('_')[1]
        label_name = callback.data.split('_')[2]
        if label_id in selected:
            del selected[label_id]
        else:
            selected[label_id] = label_name
        await state.update_data(selected=selected)
        await callback.message.edit_reply_markup(
            reply_markup=await kb.show_labels(selected)
        )
    

@expert_router.callback_query(Labelling.confirming_label, F.data == "confirm")
async def confirm_label(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]
    tooth_id = data["tooth_id"]
    selected = data["selected"].keys()
    label_ids = ", ".join(selected)

    await rq.add_answer(
        tg_id=user_id,
        tooth_id=tooth_id,
        label_ids=label_ids
    )

    new_tooth_id = int(tooth_id) + 1
    await state.update_data(selected={}, tooth_id=new_tooth_id)
    await rq.set_user_current_tooth_id(
        tg_id=data["user_id"], 
        tooth_id=new_tooth_id
    )

    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(Labelling.waiting_expert_command)
    await callback.message.answer(
        text=f'Снимок №{data["tooth_id"]}.\nРазметка успешно добавлена.',
        reply_markup=kb.label_next
    )
    

@expert_router.callback_query(Labelling.confirming_label, F.data == "go_back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Labelling.waiting_label)
    await state.update_data(selected={})
    data = await state.get_data()

    await callback.message.edit_caption(
        caption=f'Снимок №{data["tooth_id"]}.\n{LABEL_INSTRUCTIONS}',
        reply_markup=await kb.show_labels({})
    )


@expert_router.callback_query(
        F.data == "end_labelling"
)
async def end_labelling(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Labelling.waiting_expert_command)
    await state.update_data(selected={})
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
    await state.set_state(Labelling.waiting_label)
    await state.update_data(selected={})
    await callback.message.edit_reply_markup(reply_markup=None)
    
    data = await state.get_data()
    photo_path = await rq.get_tooth(data["tooth_id"])
    photo = FSInputFile(photo_path)

    if not photo:
        await callback.message.answer('Отуствуют данные для разметки.')
        return

    await callback.message.answer_photo(
        photo=photo,
        caption=f'Снимок №{data["tooth_id"]}.\n{LABEL_INSTRUCTIONS}',
        reply_markup=await kb.show_labels({})
    )    