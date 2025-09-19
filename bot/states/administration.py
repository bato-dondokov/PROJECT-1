from aiogram.fsm.state import State, StatesGroup


"""Состояния для обработки сообщений Администратора"""


class Administration(StatesGroup):
    waiting_admin_command = State()
    waiting_new_label_class = State()
    confirming_new_label_class = State()
    waiting_new_xray = State()
    confirming_new_xray = State()
    exporting_db = State()