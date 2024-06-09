from aiogram.fsm.state import StatesGroup, State

class OrderStates(StatesGroup):
    WAITING_QUANTITY_GIFT = State()
    WAITING_QUANTITY_LIMIT_ACC = State()
    WAITING_BONUS_USE = State()
    WAITING_QUANTITY = State()
    WAITING_PAYMENT = State()