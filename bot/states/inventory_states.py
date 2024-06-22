from aiogram.fsm.state import StatesGroup, State


class InventoryStates(StatesGroup):
    WAITING_INVENTORY_LIST = State()
    GET_DUMP_FILE = State()
    WAITING_INVENTORY_REMOVE = State()