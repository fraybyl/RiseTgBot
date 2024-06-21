from aiogram import types
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext


class CorrectNumberFilter(BaseFilter):
    def __init__(self, *states):
        self.states = states

    async def __call__(self, message: types.Message, state: FSMContext) -> bool:
        current_state = await state.get_state()
        if current_state not in [s.state for s in self.states]:
            return False
        try:
            number = float(message.text)
            return number < 0
        except ValueError:
            return True
