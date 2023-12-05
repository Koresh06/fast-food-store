from aiogram.fsm.state import State, StatesGroup


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

class Location1(StatesGroup):
    street = State()
    house = State()
    flat = State()

class Location2(StatesGroup):
    street = State()
    house = State()
    flat = State()



