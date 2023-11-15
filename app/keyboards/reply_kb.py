from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


async def kb_menu():
    builder = ReplyKeyboardBuilder([
        [
        KeyboardButton(text='🍔 Еда'),
        KeyboardButton(text='🛒 Корзина'),
        KeyboardButton(text='❕ О боте')   
        ],
        [  
        KeyboardButton(text='🤝 Помощь') 
        ]
    ])
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

async def kb_menu_admin():
    builder = ReplyKeyboardBuilder([
        [
        KeyboardButton(text='🍔 Еда'),
        KeyboardButton(text='🛒 Корзина'),
        KeyboardButton(text='❕ О боте')   
        ],
        [  
        KeyboardButton(text='🤝 Помощь') 
        ],
        [
        KeyboardButton(text='✳️ Добавить товар'),
        KeyboardButton(text='👑 Пользователи'),
        KeyboardButton(text='⚙️ Настройки')
        ]
    ])
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
