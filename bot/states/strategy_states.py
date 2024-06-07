from aiogram.fsm.state import StatesGroup, State

class StrategyStates(StatesGroup):
    INITIAL_ACCOUNTS = State()
    ACCOUNT_COST = State()
    WEEKLY_PROFIT = State()
    TOTAL_WEEKS = State()