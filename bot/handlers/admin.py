from aiogram import F, Router, Bot
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext

import database.requests as rq 
import keyboards.keyboards as kb
from states.administration import Administration
from xray2img import Xray2Teeth

from ultralytics import YOLO
from handlers.paths import MODELS_DIR, XRAYS_DIR, TEETH_DIR, DB_PATH

admin_router = Router()
model = YOLO(MODELS_DIR / "YOLO11m-OBB4(main)/weights/best.pt")

@admin_router.message(Administration.waiting_admin_command)
async def get_admin_command(message: Message, state: FSMContext):
    command = message.text
    if command == "Добавить класс разметки":
        await state.set_state(Administration.waiting_new_label_class)
        await message.answer(
            text='Введите название нового класса разметки',
            reply_markup=kb.go_back
        )
    elif command == "Добавить снимок":
        await state.set_state(Administration.waiting_new_xray)
        await message.answer(
            text='Отправьте снимок.',
            reply_markup=kb.go_back
        )
    if command == "Выгрузить БД":
        db_file = FSInputFile(DB_PATH)
        await message.answer_document(
            document=db_file, 
            caption="БД выгружена успешно."
        )
        await message.answer('Выберите нужную команду.')
   

@admin_router.message(Administration.waiting_new_label_class)
async def get_new_label_class(message: Message, state: FSMContext):
    await state.set_state(Administration.confirming_new_label_class)
    if message.text == "Вернуться назад":
        await state.set_state(Administration.waiting_admin_command)
        await message.answer(
            text='Выберите нужную команду.', 
            reply_markup=kb.admin_commands
        )
    else:
        label_name = message.text
        await state.update_data(label_name=label_name)
        await message.reply(
            text=f'Подтвердите добавление класса: "{label_name}".',
            reply_markup=kb.confirming
        )


@admin_router.callback_query(
        Administration.confirming_new_label_class, 
        F.data == "confirm"
)
async def confirm_new_label_class(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    label_name = data["label_name"]
    await rq.add_label(label_name)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f'Класс "{label_name}" добавлен.')
    await state.set_state(Administration.waiting_admin_command)
    await callback.message.answer(
        text='Выберите нужную команду.', 
        reply_markup=kb.admin_commands
    )


@admin_router.callback_query(
        Administration.confirming_new_label_class,
        F.data == "go_back"
)
async def go_back_admin_commands(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Administration.waiting_admin_command)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        text='Выберите нужную команду.', 
        reply_markup=kb.admin_commands
    )


@admin_router.message(
        Administration.waiting_new_xray, 
        F.text == "Вернуться назад"
)
async def get_xray(message: Message, state: FSMContext):
    await state.set_state(Administration.waiting_admin_command)
    await message.answer(
        text='Выберите нужную команду.', 
        reply_markup=kb.admin_commands
    )


@admin_router.message(Administration.waiting_new_xray, F.photo)
async def get_xray(message: Message, state: FSMContext):
    await state.set_state(Administration.confirming_new_xray)
    await state.update_data(photo_id=message.photo[-1].file_id)
    await message.reply(
        text=f'Подтвердите добавление снимка.',
        reply_markup=kb.confirming
    )
    

@admin_router.callback_query(
        Administration.confirming_new_xray, 
        F.data == "confirm"
)
async def confirm_xray(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer('Снимок обрабатывается...')

    data = await state.get_data()
    photo_file = await bot.get_file(data["photo_id"])
    xray_name = photo_file.file_unique_id
    xray_path = str(XRAYS_DIR / f"{xray_name}.png")

    await bot.download_file(photo_file.file_path, destination=xray_path)
    await rq.add_xray(xray_path)

    x2t = Xray2Teeth(xray_path, TEETH_DIR, model)
    x2t.process()
    await rq.add_teeth(TEETH_DIR, xray_name, xray_path)

    await callback.message.answer(f'Снимок добавлен.')
    await state.set_state(Administration.waiting_admin_command)
    await callback.message.answer(
        text='Выберите нужную команду.', 
        reply_markup=kb.admin_commands
    )


@admin_router.callback_query(
        Administration.confirming_new_xray,
        F.data == "go_back"
)
async def go_back_admin_commands(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Administration.waiting_admin_command)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        text='Выберите нужную команду.', 
        reply_markup=kb.admin_commands
    )