from aiogram.fsm.state import State, StatesGroup


class Register(StatesGroup):
    register_status = State()
    last_msg = State()

    full_name = State()
    phone_number = State()
    client_type = State()
    organization_name = State()
