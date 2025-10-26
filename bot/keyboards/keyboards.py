from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardRemove, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.requests import get_labels


"""Клавиатуры для бота"""


"""Удаляет ReplyKeyboard, если такая имеется"""
keyboard_remove = ReplyKeyboardRemove()


"""ReplyKeyboard клавиатура для запроса контакта пользователя."""
contact_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(
        text='Поделиться контактом', 
        request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)


"""ReplyKeyboard клавиатура для выбора роли пользователя."""
role_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Эксперт'), KeyboardButton(text='Админ')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите вашу роль.'
)


"""ReplyKeyboard клавиатура для выбора статуса пользователя."""
status_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Преподаватель'), 
               KeyboardButton(text='Ординатор')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите ваш статус.'
)


"""ReplyKeyboard клавиатура для выбора команды Администратора."""
admin_commands = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Посмотреть прогресс экспертов')],
        [KeyboardButton(text="Добавить снимок")],
        [KeyboardButton(text="Выгрузить БД")]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите нужную команду.'
)


"""
InlineKeyboard клавиатура для подтверждения действия или возврата на 
предыдущий этап.
""" 
async def confirmation_keyboard(complexity:str = '0'):
    confirming = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Подтвердить", 
                callback_data="confirm_" + complexity)],
            [InlineKeyboardButton(
                text="Вернуться назад", 
                callback_data="go_back")]
        ]
    )
    return confirming


"""ReplyKeyboard клавиатура для подтверждения команд Администратора."""
confirming_admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить", callback_data="confirm")],
        [InlineKeyboardButton(text="Вернуться назад", callback_data="go_back")]
    ]
)


"""ReplyKeyboard клавиатура для кнопки возврата на предыдущий этап."""
go_back = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Вернуться назад")]],
    resize_keyboard=True
)


"""ReplyKeyboard клавиатура для выбора команды Эксперта."""
expert_commands = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Начать разметку")]],
    resize_keyboard=True
)


"""
ReplyKeyboard клавиатура для разметки следующего снимка, либо завершение
разметки.
"""
label_next = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Разметить следующий снимок")],
        [KeyboardButton(text="Завершить разметку")]
    ]
)


"""Динамическая InlineKeyboard для выбора классов разметки."""
async def show_labels(table_name, selected_id):
    labels = await get_labels(table_name) 
    keyboard = InlineKeyboardBuilder()
    for label in labels:
        if label.name != "Сомневаюсь в ответе":
            is_selected = "✅" if str(label.id) == selected_id else ""
            keyboard.add(InlineKeyboardButton(
                text=f"{is_selected} {label.name}", 
                callback_data=f'label_{label.id}'
            ))
    if int(selected_id) > 0:
        keyboard.add(InlineKeyboardButton(
            text="--- Подтвердить ---", 
            callback_data="label_confirm"
        ))
    keyboard.add(InlineKeyboardButton(
        text="--- Сомневаюсь в ответе ---",
        callback_data="label_complex"
    ))  
    keyboard.add(InlineKeyboardButton(
        text="--- Завершить разметку ---",
        callback_data="end"
    ))
    return keyboard.adjust(1).as_markup()   