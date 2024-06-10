from aiogram.fsm.context import FSMContext

async def push_state(state: FSMContext, new_state: str):
    data = await state.get_data()
    state_stack = data.get('state_stack', [])
    state_stack.append(new_state)
    await state.update_data(state_stack=state_stack)
    await state.set_state(new_state)

async def pop_state(state: FSMContext) -> str:
    data = await state.get_data()
    state_stack = data.get('state_stack', [])
    if state_stack:
        state_stack.pop()
    if state_stack:
        previous_state = state_stack[-1]
    else:
        previous_state = None
    await state.update_data(state_stack=state_stack)
    return previous_state