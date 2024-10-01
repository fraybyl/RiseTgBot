from typing import Any

from aiogram.fsm.context import FSMContext


async def push_state(state: FSMContext, new_state: str):
    data = await state.get_data()
    state_stack = data.get('state_stack', [])
    state_stack.append(new_state)
    await state.update_data(state_stack=state_stack)
    await state.set_state(new_state)


async def pop_state(state: FSMContext) -> Any | None:
    data = await state.get_data()
    state_stack = data.get('state_stack', [])
    if len(state_stack) > 1:
        state_stack.pop()
        previous_state = state_stack[-1]
        await state.update_data(state_stack=state_stack)
        return previous_state
    elif len(state_stack) == 1:
        state_stack.pop()
        await state.update_data(state_stack=state_stack)
        await state.set_state(state=None)
        return None
    else:
        return None
