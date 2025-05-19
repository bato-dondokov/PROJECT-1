from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.requests import get_labels


keyboard_remove = ReplyKeyboardRemove()


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Эксперт'),
    KeyboardButton(text='Админ')]
],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите ваш статус.')


admin_commands = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить класс разметки')],
    [KeyboardButton(text="Добавить снимок")],
    [KeyboardButton(text="Выгрузить БД")]
],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите нужную команду.')


confirming = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Подтвердить", callback_data="confirm")],
    [InlineKeyboardButton(text="Вернуться назад", callback_data="go_back")]
])


go_back = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Вернуться назад")]],
    resize_keyboard=True,)


start_labelling = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Начать разметку")]],
    resize_keyboard=True,)


label_next = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Разметить следующий снимок")]],
    resize_keyboard=True,)

async def show_labels():
    labels = await get_labels()
    keyboard = InlineKeyboardBuilder()
    for label in labels:
        keyboard.add(InlineKeyboardButton(text=label.name, callback_data=f'label_{label.id}_{label.name}'))
    return keyboard.adjust(1).as_markup()