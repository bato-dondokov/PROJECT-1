from aiogram import F, Router, Bot
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext

from pathlib import Path

import database.requests as rq 
import keyboards.keyboards as kb
from states.administration import Administration
from xray2img import Xray2Teeth

from ultralytics import YOLO
from config import MODEL_WEIGHTS, XRAYS_DIR, TEETH_DIR, DB_FILE


admin_router = Router()
model = YOLO(MODEL_WEIGHTS)


"""
Обработчики сообщений администратора.
"""


@admin_router.message(Administration.waiting_admin_command)
async def get_admin_command(message: Message, state: FSMContext):
    """
    Обрабатывает сообщения в состоянии ожидания команд администратора
        1) "Добавить класс разметки": изменяет состояние, отправляет сообщение
        и меняет кнопки.
        2) "Добавить снимок": изменяет состояние, отправляет сообщение и 
        меняет кнопки.
        3) "Выгрузить БД": отправляет пользователю файл БД и сообщение.
    """
    command = message.text
    if command == "Добавить класс разметки":
        await state.set_state(Administration.waiting_new_label_class)
        await message.answer(
            text='Введите название нового класса разметки',
            reply_markup=kb.go_back
        )
    if command == "Добавить снимок":
        await state.set_state(Administration.waiting_new_xray)
        await message.answer(
            text='Отправьте снимок.',
            reply_markup=kb.go_back
        )
    if command == "Выгрузить БД":
        db_file = FSInputFile(DB_FILE)
        await message.answer_document(
            document=db_file, 
            caption="БД выгружена успешно."
        )
        await message.answer('Выберите нужную команду.')
   

@admin_router.message(Administration.waiting_new_label_class)
async def get_new_label_class(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение в состоянии ожидания названия нового класса 
    разметки. Отправляет пользователю сообщение и добавляет InlineKeyboard 
    для подтверждения.

    Если пользователь отправил сообщение с текстом "Вернуться назад", то
    переходит в состояние ожидания команды эксперта.
    """
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
    """
    Обрабатывает callback в состоянии подтверждения названия нового класса, 
    если callback_data == 'confirm'. Добавляет новый класс в БД, удаляет 
    inlineInlineKeyboard и переходит в состояние ожидания команды эксперта.
    """
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
    """
    Обрабатывает callback в состоянии подтверждения названия нового класса, 
    если callback_data == 'go_back'. Удаляет inlineInlineKeyboard и переходит 
    в состояние ожидания команды эксперта.
    """
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
async def go_back_admin_commands(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение в состоянии ожидания нового снимка, если сообщение 
    равно "Вернуться назад" переходит в состояние ожидания команды эксперта.
    """
    await state.set_state(Administration.waiting_admin_command)
    await message.answer(
        text='Выберите нужную команду.', 
        reply_markup=kb.admin_commands
    )


@admin_router.message(Administration.waiting_new_xray, F.photo)
async def get_xray(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение в состоянии ожидания нового снимка, если 
    пользователь отправил фото. Переходит в состояние подтверждения снимка
    """
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
    """
    Обрабатывает callback в состоянии подтверждения нового снимка, 
    если callback_data == 'confirm'. Сохраняет снимок, использует модуль для 
    обнаружения зубов на снимке (Xray2Teeth) и добавляет путь до снимка в БД. 
    После чего переходит в состояние ожидания команды эксперта.
    """    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer('Снимок обрабатывается...')

    data = await state.get_data()
    photo_file = await bot.get_file(data["photo_id"])
    xray_name = photo_file.file_unique_id
    xray_file = XRAYS_DIR + f"{xray_name}.png"

    await bot.download_file(photo_file.file_path, destination=xray_file)
    await rq.add_xray(xray_file)

    x2t = Xray2Teeth(xray_file, TEETH_DIR, model)
    x2t.process()
    await rq.add_teeth(TEETH_DIR, xray_name, xray_file)

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
    """
    Обрабатывает callback в состоянии подтверждения нового снимка, 
    если callback_data == 'go_back'. Удаляет inlineInlineKeyboard и переходит 
    в состояние ожидания команды эксперта.
    """ 
    await state.set_state(Administration.waiting_admin_command)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        text='Выберите нужную команду.', 
        reply_markup=kb.admin_commands
    )