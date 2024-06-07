from aiogram import  types
from aiogram.fsm.context import FSMContext
from aiogram.filters import BaseFilter

class MultipleStateInFilter(BaseFilter):
    def __init__(self, *states):
        self.states = states

    async def __call__(self, message: types.Message, state: FSMContext) -> bool:
        current_state = await state.get_state()
        return current_state in [s.state for s in self.states]