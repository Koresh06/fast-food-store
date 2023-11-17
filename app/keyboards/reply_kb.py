from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

import config

async def kb_menu():
    builder = ReplyKeyboardBuilder([
        [
        KeyboardButton(text='📋 Меню'),
        KeyboardButton(text='🛒 Корзина'),
        KeyboardButton(text='🤝 Помощь')    
        ]
    ])
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

async def kb_menu_admin():
    builder = ReplyKeyboardBuilder([
        [
        KeyboardButton(text='📋 Меню'),
        KeyboardButton(text='🛒 Корзина'),
        KeyboardButton(text='🤝 Помощь')    
        ],
        [
        KeyboardButton(text='✳️ Добавить товар'),
        KeyboardButton(text='👑 Пользователи'),
        KeyboardButton(text='⚙️ Настройки')
        ]
    ])
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

async def kb_menu_cart(params):
    builder = ReplyKeyboardBuilder([
        [
        KeyboardButton(text='📋 Меню'),
        KeyboardButton(text='🚕 Оформить заказ', request_location=True), 
        ]   
    ])

    for item in params:
        builder.row(KeyboardButton(text=f'❌ {params.index(item) + 1}. {item[0].strip()}. {item[1]} шт.'))
    builder.row(KeyboardButton(text='❎ Очистить корзину'))

    return builder.as_markup(resize_keyboard=True)



