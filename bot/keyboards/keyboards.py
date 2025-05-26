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


expert_commands = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Начать разметку")]],
    resize_keyboard=True,)


label_next = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Разметить следующий снимок", callback_data="label_next")],
    [InlineKeyboardButton(text="Завершить разметку", callback_data="end_labelling")]
])

async def show_labels(selected):
    labels = await get_labels()
    keyboard = InlineKeyboardBuilder()
    for label in labels:
        is_selected = "✅" if str(label.id) in selected else ""
        keyboard.add(InlineKeyboardButton(text=f"{is_selected} {label.name}", 
                                          callback_data=f'label_{label.id}_{label.name}'))
    if selected:
        keyboard.add(InlineKeyboardButton(text="Потдвердить", 
                                          callback_data="label_confirm"))
    return keyboard.adjust(1).as_markup()