from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardRemove, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.requests import get_labels, get_recommendations


"""Клавиатуры для бота"""


"""
Удаляет ReplyKeyboard, если такая имеется
"""
keyboard_remove = ReplyKeyboardRemove()


"""
ReplyKeyboard клавиатура для выбора статуса пользователя.
"""
main = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Эксперт'), KeyboardButton(text='Админ')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите ваш статус.'
)


"""
ReplyKeyboard клавиатура для выбора команды Администратора.
"""
admin_commands = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить класс разметки')],
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
confirming = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить", callback_data="confirm")],
        [InlineKeyboardButton(text="Вернуться назад", callback_data="go_back")]
    ]
)


"""
ReplyKeyboard клавиатура для кнопки возврата на предыдущий этап.
"""
go_back = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Вернуться назад")]],
    resize_keyboard=True
)


"""
ReplyKeyboard клавиатура для выбора команды Эксперта.
"""
expert_commands = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Начать разметку")]],
    resize_keyboard=True
)


"""
InlineKeyboard клавиатура для разметки следующего снимка, либо завершение
разметки.
"""
label_next = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="Разметить следующий снимок", 
            callback_data="label_next"
        )],
        [InlineKeyboardButton(
            text="Завершить разметку", 
            callback_data="end_labelling"
        )]
    ]
)


"""
Динамическая InlineKeyboard для выбора класса разметки.
"""
async def show_labels(selected):
    labels = await get_labels()
    keyboard = InlineKeyboardBuilder()
    for label in labels:
        is_selected = "✅" if str(label.id) in selected else ""
        keyboard.add(InlineKeyboardButton(
            text=f"{is_selected} {label.name}", 
            callback_data=f'label_{label.id}_{label.name}'
        ))
    if selected:
        keyboard.add(InlineKeyboardButton(
            text="--- Подтвердить ---", 
            callback_data="label_confirm"
        ))
    keyboard.add(InlineKeyboardButton(
        text="--- Завершить разметку ---",
        callback_data="end_labelling"
    ))
    return keyboard.adjust(1).as_markup()


"""
Динамическая InlineKeyboard для выбора рекомендаций к лечению.
"""
async def recommendation_keyboard(selected_id):
    recommendations = await get_recommendations()
    keyboard = InlineKeyboardBuilder()
    for rec in recommendations:
        is_selected = "✅" if str(rec.id) == selected_id else ""
        keyboard.add(InlineKeyboardButton(
            text=f"{is_selected} {rec.name}", 
            callback_data=f'rec_{rec.id}_{rec.name}'
        ))
    if int(selected_id) > 0:
        keyboard.add(InlineKeyboardButton(
            text="--- Подтвердить ---", 
            callback_data="rec_confirm"
        ))
    keyboard.add(InlineKeyboardButton(
        text="--- Завершить разметку ---",
        callback_data="end_rec"
    ))
    return keyboard.adjust(1).as_markup()