from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types.input_media_photo import InputMediaPhoto

from app.keyboards.reply_kb import *
from app.keyboards.inline_kb import *
from app.database.requests import *
from app.FSM.fsm import Location1, Location2

import config

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await chek_user(message.from_user.id, message.from_user.first_name)
    if not user:
        if await add_user(message.from_user.id, message.from_user.first_name):
            await message.answer('Вас примествует ресторан <b>FAST FOOD STORE</b>\n\n', reply_markup=await kb_menu())
            await message.bot.send_message(chat_id=config.ADMIN_ID, text=f'Новый пользователь - {message.from_user.first_name}', reply_markup=await new_user(message.from_user.id, message.from_user.first_name))
        else:
            await message.answer('Ошибка, обратитесь к администратору: https://t.me/korets_24')
    else:
        await message.answer('Доброго времени суток, мы рады вновь Вас приветствать в нашем ресторане <b>FAST FOOD STORE</b>\n\nДля работы с ботом выберите команду и меню ⬇️', reply_markup=await kb_menu())

@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Вы не заполняете форму, поэтому невозможно воспользоваться данной командой!'
    )

@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Отмена заполнения формы\n\nПри необходимости заполните форму заново'
    )
    await state.clear()


@router.message(F.text.endswith('Меню'))
async def cmd_categories_product(message: Message):
    if await output_categories():
        await message.answer('Категории', reply_markup=await user_categories())
    else:
        await message.answer('Каталог категорий пуст', reply_markup=await kb_menu())

@router.callback_query(F.data == 'bat_categ')
async def cmd_categ_back(callback: CallbackQuery):
    if await output_categories():
        await callback.message.delete()
        await callback.message.answer('Категории', reply_markup=await user_categories())
        await callback.answer()
    else:
        await callback.message.answer('Каталог пуст, для добавления нажмите ⬇️')

@router.callback_query(F.data.startswith('user_categ '))
async def cmd_fast_food(callback: CallbackQuery):
    await callback.message.delete()
    item = await output_fast_food(int(callback.data.split()[-1]))
    if item:
        await callback.message.answer_photo(item[0][1], caption=f"<b><i>Наименование:</i></b> {item[0][0]}  \n\n<b><i>Описание продукта:</i></b> {item[0][2]}\n\n<b><i>Прайс:</i></b> {item[0][3]} RUB", reply_markup=await add_cart(int(callback.data.split()[-1]), item[0][4]))
        await callback.answer()
    else:
        await callback.message.answer('На данный момент каталог продуктов пуст, загляните к нам чуть позже')
        await callback.answer()


@router.callback_query(F.data.startswith('forward'))
async def cmd_fast_food(callback: CallbackQuery):
    categ_id = int(callback.data.split('_')[-2])
    index = int(callback.data.split('_')[-1])
    item = await output_fast_food(categ_id)
    if item:
        if index < len(item) - 1:
            index += 1
            await callback.message.edit_media(media=InputMediaPhoto(media=item[index][1]))
            await callback.message.edit_caption(caption=f"<b><i>Наименование:</i></b> {item[index][0]}  \n\n<b><i>Описание продукта:</i></b> {item[index][2]}\n\n<b><i>Прайс:</i></b> {item[index][3]} RUB", reply_markup=await add_cart(categ_id, item[index][4], index))
            await callback.answer()
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=item[0][1]))
            await callback.message.edit_caption(caption=f"<b><i>Наименование:</i></b> {item[0][0]}  \n\n<b><i>Описание продукта:</i></b> {item[0][2]}   \n\n<b><i>Прайс:</i></b> {item[0][3]} RUB", reply_markup=await add_cart(categ_id, item[0][4]))
            await callback.answer()
    else:
        await callback.message.answer('На данный момент каталог продуктов пуст, загляните к нам чуть позже')
        await callback.answer()

@router.callback_query(F.data.startswith('back'))
async def cmd_fast_food(callback: CallbackQuery):
    categ_id = int(callback.data.split('_')[-2])
    index = int(callback.data.split('_')[-1])
    item = await output_fast_food(categ_id)
    if item:
        if index > 0:
            index -= 1
            await callback.message.edit_media(media=InputMediaPhoto(media=item[index][1]))
            await callback.message.edit_caption(caption=f"<b><i>Наименование:</i></b> {item[index][0]}  \n\n<b><i>Описание продукта:</i></b> {item[index][2]}\n\n<b><i>Прайс:</i></b> {item[index][3]} RUB", reply_markup=await add_cart(categ_id, item[index][4], index))
            await callback.answer()
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=item[-1][1]))
            await callback.message.edit_caption(caption=f"<b><i>Наименование:</i></b> {item[-1][0]}  \n\n<b><i>Описание продукта:</i></b> {item[-1][2]}   \n\n<b><i>Прайс:</i></b> {item[-1][3]} RUB", reply_markup=await add_cart(categ_id, item[-1][4], len(item) - 1))
            await callback.answer()
    else:
        await callback.message.answer('На данный момент каталог продуктов пуст, загляните к нам чуть позже')
        await callback.answer()

@router.callback_query(F.data.startswith('count.value'))
async def count_quanty(callback: CallbackQuery):
    current_value = int(callback.data.split('_')[-2])
    categ = int(callback.data.split('_')[-1])
    await callback.answer(text=f'Товар №{current_value} из {categ}', show_alert=True)
    await callback.answer()

@router.message(F.text.endswith('Корзина'))
async def cmd_cart(message: Message):

    items = await check_user_cart(message.from_user.id)
    if items:
        lst_menu = []
        for item in items:
            parser_product_attr = await pars_product(item[0])
            lst_menu.append(parser_product_attr)

        content = '\n➖➖➖➖➖➖➖➖➖➖➖\n'.join([f"|-🍽 {lst_menu.index(item) + 1}. {item[0][0]}\n|-{item[1]} шт. х {item[0][1]} = {item [1] * item[0][1]} BYN" for item in lst_menu])
        total_cost = sum([i[1] * i[0][1] for i in lst_menu])
        name_count_product = [(item[0][0], item[1]) for item in lst_menu]

        await message.answer(text=f'🛒 Ваша корзина:\n\n{content}\n\n💸 ИТОГО: {total_cost} RUB', reply_markup=await kb_menu_cart(name_count_product))
        
    else:
        await message.answer('Корзина пуста, перейдите в котолог [📋 Меню] и сделайте свой выбор', reply_markup=await kb_menu())

#Удаление позиций из корзины
@router.message(F.text.startswith('❌'))
async def cmd_delete_product(message: Message):
    name = message.text.split('.')[1]
    if await count_minus(name):
        items = await check_user_cart(message.from_user.id)
        if items:
            lst_menu = []
            for item in items:
                parser_product_attr = await pars_product(item[0])
                lst_menu.append(parser_product_attr)

            content = '\n➖➖➖➖➖➖➖➖➖➖➖\n'.join([f"|-🍽 {lst_menu.index(item) + 1}. {item[0][0]}\n|-{item[1]} шт. х {item[0][1]} = {item [1] * item[0][1]} BYN" for item in lst_menu])
            total_cost = sum([i[1] * i[0][1] for i in lst_menu])
            name_count_product = [(item[0][0], item[1]) for item in lst_menu]

            await message.answer(text=f'🛒 Ваша корзина:\n\n{content}\n\n💸 ИТОГО: {total_cost} RUB', reply_markup=await kb_menu_cart(name_count_product))
        else:
            await message.answer('Корзина пуста, перейдите в котолог [📋 Меню] и сделайте свой выбор')
    else:
        if await delete_menu_product(name):
            items = await check_user_cart(message.from_user.id)
            if items:
                lst_menu = []
                for item in items:
                    parser_product_attr = await pars_product(item[0])
                    lst_menu.append(parser_product_attr)

                content = '\n➖➖➖➖➖➖➖➖➖➖➖\n'.join([f"|-🍽 {lst_menu.index(item) + 1}. {item[0][0]}\n|-{item[1]} шт. х {item[0][1]} = {item[1] * item[0][1]} BYN" for item in lst_menu])
                total_cost = sum([i[1] * i[0][1] for i in lst_menu])
                name_count_product = [(item[0][0], item[1]) for item in lst_menu]

                await message.answer(text=f'🛒 Ваша корзина:\n\n{content}\n\n💸 ИТОГО: {total_cost} RUB', reply_markup=await  kb_menu_cart(name_count_product))
            else:
                await message.answer('Корзина пуста, перейдите в котолог [📋 Меню] и сделайте свой выбор', reply_markup=await kb_menu())

@router.message(F.text.endswith('Очистить корзину'))
async def clear_cart(message: Message):
    if await clear_cart_pr(message.from_user.id):
        await message.answer('Корзина очищена, для пополнения переёдите в 📋 Меню)', reply_markup=await kb_menu())
    else:
        await message.answer('Ошибка, обратитесь к администратору [🤝 Помощь]')
    

#Уменьшение количества товара, при попытке уменьшить меньше еденицы товар удаляется из корзины и переход в исходную клаву
@router.callback_query(F.data.endswith('minus'))
async def cmd_minus(callback: CallbackQuery):
    id_categ = int(callback.data.split('_')[0])
    id_product = int(callback.data.split('_')[1])
    index = int(callback.data.split('_')[2])
    if await minus_count_product(id_product):
        await callback.message.edit_reply_markup(reply_markup=await user_cart_product(id_categ, id_product, index))
    else:
        await delete_cart(callback.from_user.id, id_product)
        await callback.message.edit_reply_markup(reply_markup=await add_cart(id_categ, id_product, index))

#Добавление количества товара, максимальное количество 10 шт.
@router.callback_query(F.data.endswith('plus'))
async def cmd_minus(callback: CallbackQuery):
    id_categ = int(callback.data.split('_')[0])
    id_product = int(callback.data.split('_')[1])
    index = int(callback.data.split('_')[2])
    if await plus_count_product(id_product):
        await callback.message.edit_reply_markup(reply_markup=await user_cart_product(id_categ, id_product, index))
    else:
        await callback.answer('Максимальное количество 10 шт.')

@router.callback_query(F.data.endswith('count'))
async def cmd_minus(callback: CallbackQuery):
    check_count = await check_quantuty(int(callback.data.split()[0]))
    await callback.answer(f'У вас в корзине 🛒 {check_count} шт.')
    await callback.answer()


#При изменении количества изменяется клава
@router.callback_query(F.data.endswith('add_cart'))
async def cmd_add_cart(callback: CallbackQuery):
    id_categ = int(callback.data.split('_')[0])
    id_product = int(callback.data.split('_')[1])
    index = int(callback.data.split('_')[2])
    if await add_cart_product(callback.from_user.id, id_product):
        await callback.message.edit_reply_markup(reply_markup=await user_cart_product(id_categ, id_product, index))
        await callback.answer(text='Товар добавлен в корзину')
    else:
        await callback.answer('Товар уже был добавлен в корзину', show_alert=True)
    

@router.message(F.text.endswith('Помощь'))
async def cmd_help(message: Message):
    await message.answer('🔸У вас возникли вопросы?\nМы с удовольствием ответим!\n', reply_markup=kb_help)


#Оплата корзины
@router.message(F.text.endswith('Оформить заказ'))
async def place_an_order(message: Message):
    await message.answer(text='Выберете пункт меню:', reply_markup=payment_kb)

@router.callback_query(StateFilter(default_state), F.data == 'order1')
async def manual_address(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer('Укажите улицу:\n\n❌ Отмена - /cancel')
    await state.set_state(Location1.street)
    await callback.answer()

@router.message(StateFilter(Location1.street))
async def user_street(message: Message, state: FSMContext):
    await state.update_data(street=message.text)
    await message.answer('Укажите номер дома:\n\n❌ Отмена - /cancel')
    await state.set_state(Location1.house)

@router.message(StateFilter(Location1.house))
async def user_house(message: Message, state: FSMContext):  
    await state.update_data(house=message.text)
    await message.answer('Укажите номер квартиры:\n\n❌ Отмена - /cancel')
    await state.set_state(Location1.flat)

@router.message(StateFilter(Location1.flat))
async def payment_by_card(message: Message, state: FSMContext):
    await state.update_data(flat=message.text)
    address = await state.get_data()
    payment_con = await payment_cart(message.from_user.id)
    quantity = [item[1] for item in payment_con]
    content = [await product_name_desc_price(item[0]) for item in payment_con]
    price = [item[0][1] for item in content]
    name_prod = [item[0][0] for item in content]
    desc_name_quantity = dict(zip(name_prod, quantity))
    total_cost = sum([float(i * quantity[idx])  for idx, i in enumerate(price)])
    address_d = f'{address["street"]}/{address["house"]}/{address["flat"]}'
    text_desc_address = f'Доставка по адресу: ул.{address["street"]}, д.{address["house"]}, кв.{address["flat"]}'
    desc_product = '; '.join(f'{key}: {value}шт.' for key, value in desc_name_quantity.items())

    #Сохранение в БД заказа
    try:
        await save_order(message.from_user.id, address_d, desc_name_quantity, total_cost)
    except Exception as ex:
        price(ex)
    finally:
        await state.clear()

    id_tovar = await tovar_last(message.from_user.id)
    data_id = int(id_tovar[-1][0])

    await message.answer('Тестовая карта\n\nНомер карты: 1111 1111 1111 1026\nММ/ГГ: 12/22\nCVC: 000\n\nДанная карта предназначена только для тестирования платежной системы!')

    await message.answer_invoice(title=text_desc_address, description=desc_product, payload=f'month_sub_{data_id}', provider_token=config.TOKEN_YOUCASSA, currency='RUB', start_parameter='test_pay', prices=[{'label': 'Руб', 'amount': f"{total_cost * 100:.2f}"}])


    await state.clear()

@router.callback_query(StateFilter(default_state), F.data == 'order2')
async def manual_address(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer('Укажите улицу:\n\n❌ Отмена - /cancel')
    await state.set_state(Location2.street)
    await callback.answer()

@router.message(StateFilter(Location2.street))
async def user_street(message: Message, state: FSMContext):
    await state.update_data(street=message.text)
    await message.answer('Укажите номер дома:\n\n❌ Отмена - /cancel')
    await state.set_state(Location2.house)

@router.message(StateFilter(Location2.house))
async def user_house(message: Message, state: FSMContext):  
    await state.update_data(house=message.text)
    await message.answer('Укажите номер квартиры:\n\n❌ Отмена - /cancel')
    await state.set_state(Location2.flat)

@router.message(StateFilter(Location2.flat))
async def payment_after_receipt(message: Message, state: FSMContext):
    await state.update_data(flat=message.text)
    address = await state.get_data()
    payment_con = await payment_cart(message.from_user.id)
    quantity = [item[1] for item in payment_con]
    content = [await product_name_desc_price(item[0]) for item in payment_con]
    price = [item[0][1] for item in content]
    name_prod = [item[0][0] for item in content]
    desc_name_quantity = dict(zip(name_prod, quantity))
    total_cost = sum([float(i * quantity[idx])  for idx, i in enumerate(price)])
    address_d = f'{address["street"]}/{address["house"]}/{address["flat"]}'
    text_desc_address = f'Доставка по адресу: ул.{address["street"]}, д.{address["house"]}, кв.{address["flat"]}'
    desc_product = ';\n'.join(f'{key}: {value}шт.' for key, value in desc_name_quantity.items())

    await message.answer(f"{text_desc_address}\n\nВаш заказ:{desc_product}\n\nОБЩАЯ СУММА: {total_cost * 100:.2f} RUB")

    #Сохранение в БД заказа
    try:
        await save_order(message.from_user.id, address_d, desc_name_quantity, total_cost)
        await clear_cart_pr(message.from_user.id)
        id_order = await last_order(message.from_user.id)
        index = id_order.all()[-1][0]
        content = await desc_order(index)
        content = content[0]
        pos = '\n'.join([f'{k}: {v} шт.' for k, v in content[3].items()])
        await message.bot.send_message(chat_id=config.ADMIN_ID, text=f'Новый заказ от {message.from_user.first_name}\n\n{content[1]}\n\n{pos}\n\n💸 ОБЩАЯ СТОИМОСТЬ: {content[4]} RUB\n\n♻️ СТАТУС ОПЛАТЫ: {content[5]}', reply_markup=await kb_state_1(index, message.from_user.id))
    except Exception as ex:
        price(ex)
    finally:
        await state.clear()

    await state.clear()
    await message.answer('Товар оформлем!\n\nОжидайте... Адинистратор с Вами свяжеться', reply_markup=await kb_menu())

@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout: types.PreCheckoutQuery):
    await pre_checkout.answer(ok=True)

@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_pay(message: Message):
    if message.successful_payment.invoice_payload.startswith('month_sub'):
        index = message.successful_payment.invoice_payload.split('_')[-1]
        await payment_confirmation(message.from_user.id, int(index))
        await clear_cart_pr(message.from_user.id)
        content = await desc_order(index)
        content = content[0]
        pos = '\n'.join([f'{k}: {v} шт.' for k, v in content[3].items()])
        await message.bot.send_message(chat_id=config.ADMIN_ID, text=f'Новый заказ от {message.from_user.first_name}\n\n{content[1]}\n\n{pos}\n\n💸 ОБЩАЯ СТОИМОСТЬ: {content[4]} RUB\n\n♻️ СТАТУС ОПЛАТЫ: {content[5]}', reply_markup=await kb_state_1(index, message.from_user.id))
        await message.answer('Товар оформлен и оплачен!\n\nОжидайте... Адинистратор с Вами свяжеться', reply_markup=await kb_menu())
    elif message.successful_payment.invoice_payload.startswith('pay_order/'):
        ord_id = message.successful_payment.invoice_payload.split('/')[-1]
        if await flag_payment(ord_id):
            await message.answer('Оплата произведена успешно ✅', reply_markup=await kb_menu())
        

@router.message(F.text.endswith('Мои заказы'))
async def my_orders(message: Message):
    orders = await lst_my_orders(message.from_user.id)
    if orders:

        await message.answer('Мои заказы!\n🟢 - Оплачено   🔴 - Не оплачено', reply_markup=await kb_my_orders(orders))
    else:
        await message.answer('<b>На данный момент Вы не имеете заказов</b>\n\nДля оформления заказа перейдите в 📋 Меню', reply_markup=await kb_menu())

@router.callback_query(F.data.startswith('cancle-order'))
async def my_orders(callback: CallbackQuery):
    user_id = int(callback.data.split('_')[-1])
    orders = await cancle_my_orders(user_id)
    if orders:
        await callback.message.edit_text('Мои заказы!\n🟢 - Оплачено   🔴 - Не оплачено', reply_markup=await kb_my_orders(orders))
    else:
        await callback.message.answer('<b>На данный момент Вы не имеете заказов</b>\n\nДля оформления заказа перейдите #в 📋 Меню', reply_markup=await kb_menu())

@router.callback_query(F.data.startswith('ordders_'))
async def ordders_(callback: CallbackQuery):
    id_order = int(callback.data.split('_')[-1])
    user_id = int(callback.data.split('_')[-2])
    content = await desc_order(id_order)
    content = content[0]
    pos = '\n'.join([f'{k}: {v} шт.' for k, v in content[3].items()])
    await callback.message.edit_text(f'{content[1]}\n\n{pos}\n\nОБЩАЯ СТОИМОСТЬ: {content[4]} RUB', reply_markup=await one_pos_order(content[0], content[5], user_id))
    await callback.answer()

@router.callback_query(F.data.startswith('pay_'))
async def order_payment_one(callback: CallbackQuery):
    await callback.message.delete()
    id_ = int(callback.data.split('_')[-1])
    content = await pay_content(id_)
    
    sp_address = content[0].split('/')
    address = f'ул.{sp_address[0]}, д.{sp_address[1]}, кв.{sp_address[2]}'
    order = ', '.join([f'{k}: {v} шт.' for k, v in content[1].items()])

    await callback.message.answer_invoice(title=address, description=order, payload=f'pay_order/{id_}', provider_token=config.TOKEN_YOUCASSA, currency='RUB', start_parameter='test_pay', prices=[{'label': 'Руб', 'amount': f"{content[2] * 100:.2f}"}])



@router.message()
async def cmd_echo(message: Message):
    await message.answer('Данная команда/текст находится в разработке или вы пишите какую-то ерунду и бот Вас не понимает 🥴')