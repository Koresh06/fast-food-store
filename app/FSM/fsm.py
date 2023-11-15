from aiogram.fsm.state import State, StatesGroup

class Update_user(StatesGroup):
    first_name = State()
    last_name = State()
    phone_number = State()

class Add_categories(StatesGroup):
    name = State()

class Update_product(StatesGroup):
    name = State()
    image = State()
    description = State()
    price =  State()

class OutputProduct(StatesGroup):
    categor_id = State()
    product_index = State()


