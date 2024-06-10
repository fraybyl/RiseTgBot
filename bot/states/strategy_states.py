from aiogram.fsm.state import StatesGroup, State

class StrategyStates(StatesGroup):
    INITIAL_ACCOUNTS = State()
    TOTAL_WEEKS = State()
    CALCULATE = State()