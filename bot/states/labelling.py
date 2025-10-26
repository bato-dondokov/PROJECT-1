from aiogram.fsm.state import State, StatesGroup


"""Состояния для разметки"""


class Labelling(StatesGroup):
    waiting_expert_command = State()
    labelling = State()
    confirming_label = State()