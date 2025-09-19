from aiogram.fsm.state import State, StatesGroup


"""Состояния для разметки"""


class Labelling(StatesGroup):
    waiting_expert_command = State()
    waiting_label = State()
    confirming_label = State()
    waiting_recommendation = State()
    confirming_rec = State()