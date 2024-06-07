from aiogram.fsm.state import StatesGroup, State

class OrderStates(StatesGroup):
    WAITING_QUANTITY_GIFT = State()
    WAITING_QUANTITY_LIMIT_ACC = State()
    WAITING_PAYMENT = State()