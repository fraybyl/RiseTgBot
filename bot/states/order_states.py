from aiogram.fsm.state import StatesGroup, State


class OrderStates(StatesGroup):
    WAITING_PRODUCT_QUANTITY = State()
    WAITING_BONUS_QUANTITY = State()
    WAITING_PAYMENT = State()
