from aiogram.fsm.state import State, StatesGroup


class Labelling(StatesGroup):
    waiting_expert_command = State()
    waiting_label = State()
    confirming_label = State()