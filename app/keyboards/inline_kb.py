from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.requests import *

async def add_cart(id_categ, id_product, index=0):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='🛒 Добавить в корзину', callback_data=f'{id_product}_add_cart'))
    count_quant = await count_quantuty(id_categ)
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

order = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='♻️ Обновить корзину', callback_data='update')],
        [InlineKeyboardButton(text='Оформить заказ', callback_data='order')]
    ]
)

#async def bat_product_cart(product_id):
#    count_product = await check_quantuty(product_id)
#    builder = InlineKeyboardBuilder([
#        [
#            InlineKeyboardButton(text='🔽', callback_data=f'{product_id} minus'),
#            InlineKeyboardButton(text=f'🛒 {count_product} шт.', callback_data=f'{product_id} count'),
#            InlineKeyboardButton(text='🔼', callback_data=f'{product_id} plus')
#        ]
#    ])
#    builder.row(InlineKeyboardButton(text='🚫 Удалить', callback_data=f'{product_id}_delete'))
#    return builder.as_markup()

async def user_cart_product(id_product):
    builder = InlineKeyboardBuilder()

    for item in id_product:
        check = await inline_kb_product(item[0])
        count_product = await check_quantuty(item[0])
        builder.row(InlineKeyboardButton(text=f'{check[0][0]}', callback_data=f'user_cart {item[0]}'), width=1)
        builder.row(
            InlineKeyboardButton(text='🔽', callback_data=f'{item[0]} minus'),
            InlineKeyboardButton(text=f'🛒 {count_product} шт.', callback_data=f'{item[0]} count'),
            InlineKeyboardButton(text='🔼', callback_data=f'{item[0]} plus'),
            InlineKeyboardButton(text='🚫', callback_data=f'{item[0]}_delete'),
            width=4

        )
        
    return builder.as_markup()

async def update_in_bt(id_pr):
    builder = InlineKeyboardBuilder()
    check = await inline_kb_product(id_pr)
    count_product = await check_quantuty(id_pr)
    builder.row(InlineKeyboardButton(text=f'{check[0][0]}', callback_data=f'user_cart {id_pr}'), width=1)
    builder.row(
        InlineKeyboardButton(text='🔽', callback_data=f'{id_pr} minus'),
        InlineKeyboardButton(text=f'🛒 {count_product} шт.', callback_data=f'{id_pr} count'),
        InlineKeyboardButton(text='🔼', callback_data=f'{id_pr} plus'),
        InlineKeyboardButton(text='🚫', callback_data=f'{id_pr}_delete'),
        width=4

    )

    return builder.as_markup()
