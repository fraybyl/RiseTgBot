from aiogram.fsm.state import StatesGroup, State


class AdminState(StatesGroup):
    ADMIN_MESSAGE = State()
