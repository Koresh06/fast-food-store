from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.requests import *

async def add_cart(id_categ, id_product, index=0):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='🛒 Добавить в корзину', callback_data=f'{id_categ}_{id_product}_{index}_add_cart'))
    count_quant = await count_quantuty(id_categ)
    builder.row(InlineKeyboardButton(text='« Назад', callback_data=f'back_{id_categ}_{index}'),
                InlineKeyboardButton(text=f'{index + 1}/{count_quant}', callback_data=f'count.value_{index + 1}_{count_quant}'),
                InlineKeyboardButton(text='Вперед »', callback_data=f'forward_{id_categ}_{index}'))
    builder.row(InlineKeyboardButton(text='⬅️ Каталог', callback_data='bat_categ'))
    return builder.as_markup()

async def user_cart_product(id_categ, id_product, index=0):
    builder = InlineKeyboardBuilder()

    count_product = await check_quantuty(id_product)
    count_quant = await count_quantuty(id_categ)
    builder.row(
        InlineKeyboardButton(text='🔽', callback_data=f'{id_categ}_{id_product}_{index}_minus'),
        InlineKeyboardButton(text=f'🛒 {count_product} шт.', callback_data=f'{id_product} count'),
        InlineKeyboardButton(text='🔼', callback_data=f'{id_categ}_{id_product}_{index}_plus'),
        )
    builder.row(InlineKeyboardButton(text='« Назад', callback_data=f'back_{id_categ}_{index}'),
                InlineKeyboardButton(text=f'{index + 1}/{count_quant}', callback_data=f'count.value_{index + 1}_{count_quant}'),
                InlineKeyboardButton(text='Вперед »', callback_data=f'forward_{id_categ}_{index}'))
    builder.row(InlineKeyboardButton(text='⬅️ Каталог', callback_data='bat_categ'))
        
    return builder.as_markup()

async def user_categories():
    cat = await output_categories()
    builder = InlineKeyboardBuilder()
    for i in cat:
        builder.row(InlineKeyboardButton(text=i[0], callback_data=f'user_categ {i[1]}'))
    builder.adjust(1)
    return builder.as_markup()

async def categories():
    cat = await output_categories()
    builder = InlineKeyboardBuilder()
    for i in cat:
        builder.row(InlineKeyboardButton(text=i[0], callback_data=f'categ_{str(i[1])}'))
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text='Добавить категорию', callback_data='add_categor'))
    return builder.as_markup()

non_categor = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Добавить категорию', callback_data='add_categor')]
    ]
)


kb_help = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Администратор', url='https://t.me/korets_24')]
    ]
)

payment_kb= InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='💳 Оплатить сейчас', callback_data='order1')],
        [InlineKeyboardButton(text='🎁 Оплатить после получения заказа', callback_data='order2')]
    ]
)

async def users_inline_buttons():
    but = await users()
    
    builder = InlineKeyboardBuilder()
    for item in but:
        builder.add(InlineKeyboardButton(text=item[0], url=f'tg://user?id={item[1]}'))
    builder.adjust(1)
    return builder.as_markup()


