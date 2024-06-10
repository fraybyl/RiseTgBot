from aiogram.fsm.state import StatesGroup, State

class OrderStates(StatesGroup):
    WAITING_QUANTITY = State()
    WAITING_CONFIRMATION = State()
    WAITING_BONUS_USE = State()
    WAITING_PAYMENT = State()
    