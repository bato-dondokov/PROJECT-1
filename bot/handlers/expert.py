from aiogram import F, Router, Bot
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext

import keyboards.keyboards as kb
import database.requests as rq 
from states.labelling import Labelling


expert_router = Router()


@expert_router.message(Labelling.waiting_expert_command, 
                       (F.text == "Начать разметку") | (F.text == "Разметить следующий снимок"))
async def start_labelling(message: Message, state: FSMContext):
    await state.set_state(Labelling.waiting_label)

    current_tooth_id = await rq.get_user_current_tooth_id(message.from_user.id)
    tooth_file_path = await rq.get_tooth(current_tooth_id)

    await state.update_data(tg_id=message.from_user.id,
                            tooth_id=current_tooth_id)

    photo = FSInputFile(tooth_file_path)
    await message.answer_photo(photo=photo,
                                caption=f'Снимок №{current_tooth_id}.\n' \
    'Выберите подходящий вариант разметки.',
                                reply_markup=await kb.show_labels())


@expert_router.callback_query(Labelling.waiting_label,
                             F.data.startswith("label_"))
async def get_label(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Labelling.confirming_label)
    label_id = callback.data.split('_')[1]
    label_name = callback.data.split('_')[2]
    await state.update_data(label_id=label_id)
    await callback.message.edit_caption(caption=f"Подтвердите свой выбор: {label_name}.",
                            reply_markup=kb.confirming)
    

@expert_router.callback_query(Labelling.confirming_label, 
                              F.data == "confirm")
async def confirm_label(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await rq.add_answer(tg_id=data["tg_id"],
                        tooth_id=data["tooth_id"],
                        label_id=data["label_id"])
    new_tooth_id = int(data["tooth_id"]) + 1
    await rq.set_user_current_tooth_id(tg_id=data["tg_id"],
                                       tooth_id=new_tooth_id)
    print(new_tooth_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(Labelling.waiting_expert_command)
    await callback.message.answer(text=f'Снимок №{data["tooth_id"]}.\nРазметка успешно добавлена.',
                                  reply_markup=kb.label_next)