from aiogram.fsm.state import StatesGroup, State


class AdminState(StatesGroup):
    ADMIN_MESSAGE= State()
    ADD_CATEGORY_STATE= State()
    ADD_PHOTO_FILENAME_STATE = State()
    DELETE_CATEGORY_STATE = State()
    MAILING_LIST_STATE= State()