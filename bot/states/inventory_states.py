from aiogram.fsm.state import StatesGroup, State

class InventoryStates(StatesGroup):
    WAITING_INVENTORY_LIST = State()