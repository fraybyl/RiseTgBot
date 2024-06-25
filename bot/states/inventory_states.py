from aiogram.fsm.state import StatesGroup, State


class InventoryStates(StatesGroup):
    WAITING_ADD_ACCOUNTS = State()
    WAITING_REMOVE_ACCOUNTS = State()