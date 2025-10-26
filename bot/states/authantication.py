from aiogram.fsm.state import State, StatesGroup


"""Состояния для авторизации"""


class Authentication(StatesGroup):
    waiting_contact = State()
    waiting_user_role = State()
    waiting_user_status = State()
    waiting_password = State()