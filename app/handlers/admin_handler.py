from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from app.keyboards.reply_kb import kb_menu_admin
from app.keyboards.inline_kb import *
from app.database.requests import *
from app.FSM.fsm import Update_product, Add_categories
from app.filters.filter import CheckImageFilter, IsDigitFilter
from app.middlewares.middlewares import Is_Admin

import copy


admin = Router()

admin.message.middleware(Is_Admin())

@admin.message(Command('admin'), StateFilter(default_state))
async def cmd_admin(message: Message):
    await message.answer('Привет хозяин', reply_markup=await kb_menu_admin())

@admin.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='🚫 Отмена заполнения формы\n\nПри необходимости заполните форму заново'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()
    
@admin.message(F.text.endswith('Добавить товар'))
async def cmd_add_product(message: Message):
    if await output_categories():
        await message.answer('Категории', reply_markup=await categories())
    else:
        await message.answer('Каталог категорий пуст, для добавления нажмите ⬇️', reply_markup=non_categor)

@admin.callback_query(F.data == 'add_categor', StateFilter(default_state))
async def but_add_categ(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите название категории:\n\n❌ Отмена - /cancel')
    await state.set_state(Add_categories.name)
    await callback.answer()

@admin.message(StateFilter(Add_categories.name))
async def cmd_categ_name(message: Message, state: FSMContext):
    data = await state.update_data(name=message.text)
    if await add_categories(data['name']):
        await message.answer('✅ Категория добавлена успешно\n\n❌ Отмена - /cancel')
        await state.clear()
    else:
        await message.answer('🚫 Данная категория уже была добавлена', reply_markup=await kb_menu_admin())
        await state.clear()

@admin.callback_query(F.data.startswith('categ_'), StateFilter(default_state))
async def product_categ(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите название товара:\n\n❌ Отмена - /cancel')
    await state.set_state(Update_product.name)
    await state.update_data(id_categ=int(callback.data[-1]))
    await callback.answer()

@admin.message(StateFilter(Update_product.name))
async def cmd_name_product(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Загрузите изображение товара:\n\n❌ Отмена - /cancel')
    await state.set_state(Update_product.image)

@admin.message(StateFilter(Update_product.image), CheckImageFilter())
async def cmd_image_product(message: Message, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await message.answer('Введите описание товара:\n\n❌ Отмена - /cancel')
    await state.set_state(Update_product.description)

@admin.message(StateFilter(Update_product.description))
async def cmd_description_product(messsage: Message, state: FSMContext):
    await state.update_data(description=messsage.text)
    await messsage.answer('Введите прайс/цену товара:\n\n❌ Отмена - /cancel')
    await state.set_state(Update_product.price)

@admin.message(StateFilter(Update_product.price), IsDigitFilter())
async def cmd_price_product(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    product = await state.get_data()
    await message.answer_photo(product['image'])
    await message.answer(f"<b><i>Наименование:</i></b> {product['name']}\n\n<b><i>Описание продукта:</i></b> {product['description']}\n\n<b><i>Прайс:</i></b> {product['price']} BYN")
    if await add_product_db(message.from_user.id, product):
        await message.answer('✅ Товар успешно добавлен', reply_markup=await kb_menu_admin())
        await state.clear()
    else:
        await message.answer('❌ Произошла ошибка')
        await state.clear()

@admin.message(F.text.endswith('Заказы'))
async def admin_state_cmd(message: Message):
    await message.answer('Состояния заказов', reply_markup=await admin_orders())

@admin.callback_query(F.data == 'cancle_state')
async def admin_state_cmd(callback: CallbackQuery):
    await callback.message.edit_text('Состояния заказов', reply_markup=await admin_orders())

@admin.callback_query(F.data.startswith('1_ordstate'))
async def state_cmd(callback: CallbackQuery):
    state = int(callback.data.split("_")[0])
    try:
        if state == 1:
            order = await ordstate_1()
            user = await tg_id_username(order[0][1])
            pos = '\n'.join([f'{k}: {v} шт.' for k, v in order[0][3].items()])
            await callback.message.edit_text(f'Новый заказ от {user[1]}\n\n{order[0][2]}\n\n{pos}\n\n💸ОБЩАЯСТОИМОСТЬ: {order[0][4]} RUB\n\n♻️СТАТУС ОПЛАТЫ: {"✅" if order[0][5] else "❌"}', reply_markup=await state1_admin(order[0][0], user[0], len(order)))
        elif state == 2:
            pass
        elif state == 3:
            pass
    except Exception as ex:
        print(ex)

@admin.callback_query(F.data.startswith('admin_'))
async def adminback_cmd(callback: CallbackQuery):
    cmd = callback.data.split('_')[1]
    index = int(callback.data.split('_')[-1])
    order = await ordstate_1()
    try:
        if cmd == 'back':
            if index > 0:
                index -= 1
                user = await tg_id_username(order[index][1])
                pos = '\n'.join([f'{k}: {v} шт.' for k, v in order[index][3].   items()])
                await callback.message.edit_text(f'Новый заказ от {user[1]}\n\n{order[index][2]}\n\n{pos}\n\n💸 ОБЩАЯ СТОИМОСТЬ: {order [index][4]} RUB\n\n♻️ СТАТУС ОПЛАТЫ: {"✅" if order[index][5] else "❌"}', reply_markup= await state1_admin(order[index][0], user[0], len(order), index))
            else:
                user = await tg_id_username(order[-1][1])
                pos = '\n'.join([f'{k}: {v} шт.' for k, v in order[-1][3].  items()])
                await callback.message.edit_text(f'Новый заказ от {user[1]}\n\n{order[-1][2]}\n\n{pos}\n\n💸 ОБЩАЯ СТОИМОСТЬ: {order[-1]    [4]} RUB\n\n♻️ СТАТУС ОПЛАТЫ: {"✅" if order[-1][5] else "❌"}', reply_markup= await state1_admin(order[-1][0], user[0], len(order), len(order) - 1))
        elif cmd == 'forward':
            if index < len(order) - 1:
                index += 1
                user = await tg_id_username(order[index][1])
                pos = '\n'.join([f'{k}: {v} шт.' for k, v in order[index][3].items()])
                await callback.message.edit_text(f'Новый заказ от {user[1]}\n\n{order[index][2]}\n\n{pos}\n\n💸 ОБЩАЯ СТОИМОСТЬ: {order [index][4]} RUB\n\n♻️ СТАТУС ОПЛАТЫ: {"✅" if order[index][5]else "❌"}', reply_markup= await state1_admin(order[index][0], user[0], len(order), index))
            else:
                user = await tg_id_username(order[0][1])
                pos = '\n'.join([f'{k}: {v} шт.' for k, v in order[0][3].items()])
                await callback.message.edit_text(f'Новый заказ от {user[1]}\n\n{order[0][2]}\n\n{pos}\n\n💸 ОБЩАЯ СТОИМОСТЬ: {order[0][4]} RUB\n\n♻️ СТАТУС ОПЛАТЫ: {"✅" if order[0][5] else "❌"}', reply_markup= await state1_admin(order[0][0], user[0], len(order)))
    except Exception as ex:
        print(ex)


@admin.callback_query(F.data.startswith('state1'))
async def state1_cmd(callback: CallbackQuery):
    index = int(callback.data.split('_')[-2])
    tg_id = int(callback.data.split('_')[-1])
    if await state1_order(index):
        await callback.message.bot.send_message(chat_id=tg_id, text=f'Администратор подтвердил ваш заказ № {index}')
        await callback.message.delete()
        await callback.answer()
    else:
        await callback.message.answer('Ошибка!')
        await callback.answer()

@admin.callback_query(F.data.startswith('1_state_admin'))
@admin.callback_query(F.data.startswith('del_'))
async def delete_order_cmd(callback: CallbackQuery):
    index = int(callback.data.split('_')[-2])
    tg_id = int(callback.data.split('_')[-1])
    if await delete_orders(index):
        if callback.data.startswith('del_'):
            await callback.answer('Заказ оклонен!')
            await callback.message.bot.send_message(chat_id=tg_id, text=f'Ваш заказ № {index} откланен администратором')
        elif callback.data.startswith('1_state_admin'):
            await callback.message.bot.send_message(chat_id=tg_id, text=f'Администратор подтвердил ваш заказ № {index}')
        try:
            order = await ordstate_1()
            user = await tg_id_username(order[0][1])
            pos = '\n'.join([f'{k}: {v} шт.' for k, v in order[0][3].items()])
            await callback.message.edit_text(f'Новый заказ от {user[1]}\n\n{order[0][2]}\n\n{pos}\n\n💸 ОБЩАЯ СТОИМОСТЬ:   {order[0][4]}   RUB\n\n♻️СТАТУС ОПЛАТЫ: {"✅" if order[0][5] else "❌"}', reply_markup=await state1_admin(order[0][0], user[0], len(order)))
        except IndexError as ex:
            await callback.message.edit_text('Состояния заказов', reply_markup=await admin_orders())
            print(ex)
    else:
        await callback.message('Ошибка!')

@admin.message(F.text.endswith('Пользователи'))
async def settings_admin(message: Message):
    if await users():
        await message.answer(text='👑 Пользователи', reply_markup=await users_inline_buttons())
    else:
        await message.answer('Пользователи отсутствуют')



