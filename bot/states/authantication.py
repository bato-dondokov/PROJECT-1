from aiogram.fsm.state import State, StatesGroup


class Authentication(StatesGroup):
    waiting_user_status = State()
    waiting_password = State()