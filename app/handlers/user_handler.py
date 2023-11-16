from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.methods.delete_message import DeleteMessage

from app.keyboards.reply_kb import *
from app.keyboards.inline_kb import *
from app.database.requests import *
from app.FSM.fsm import Update_user

router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def cmd_start(message: Message, state: FSMContext):
    user = await chek_user(message.from_user.id, message.from_user.first_name)
    if not user:
        await message.answer('Вас примествует ресторан <b>FAST FOOD STORE</b>\n\nЧтобы оформить Ваш первый заказ, для начала давайте пройдем регистрацию')
        await message.answer('Укажите своё имя:')
        await state.set_state(Update_user.first_name)
    else:
        await message.answer('Доброго времени суток, мы рады Вас приветствать в нашем ресторане <b>FAST FOOD STORE</b>\n\nДля работы с ботом выберите команду и меню ⬇️', reply_markup=await kb_menu())

@router.message(StateFilter(Update_user.first_name))
async def reg_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer('Укажите фамилию:')
    await state.set_state(Update_user.last_name)

@router.message(StateFilter(Update_user.last_name))
async def reg_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer('Укажите номер телефона для связи с Вами:')
    await state.set_state(Update_user.phone_number)

@router.message(StateFilter(Update_user.phone_number))
async def reg_first_name(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    contact = await state.get_data()
    if await add_user(message.from_user.id, message.from_user.first_name, contact):
        await message.answer('✅ Регистрация прошла успешно!')
        await state.clear()
        await message.answer('Воспользуйтесь меню для работы с ботом ⤵️', reply_markup=await kb_menu())
    else:
        await message.answer('❌ Произошла ошибка')
        await state.clear()


@router.message(F.text.endswith('Еда'))
async def cmd_categories_product(message: Message):
    if await output_categories():
        await message.answer('Категории', reply_markup=await user_categories())
    else:
        await message.answer('Каталог категорий пуст')

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
        await callback.message.answer_photo(item[0][1], caption=f"<b><i>Наименование:</i></b> {item[0][0]}  \n\n<b><i>Описание продукта:</i></b> {item[0][2]}\n\n<b><i>Прайс:</i></b> {item[0][3]} BYN", reply_markup=await add_cart(int(callback.data.split()[-1]), item[0][4]))
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
            await callback.message.edit_caption(caption=f"<b><i>Наименование:</i></b> {item[index][0]}  \n\n<b><i>Описание продукта:</i></b> {item[index][2]}\n\n<b><i>Прайс:</i></b> {item[index][3]} BYN", reply_markup=await add_cart(categ_id, item[index][4], index))
            await callback.answer()
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=item[0][1]))
            await callback.message.edit_caption(caption=f"<b><i>Наименование:</i></b> {item[0][0]}  \n\n<b><i>Описание продукта:</i></b> {item[0][2]}   \n\n<b><i>Прайс:</i></b> {item[0][3]} BYN", reply_markup=await add_cart(categ_id, item[0][4]))
            await callback.answer()
    else:
        await callback.message.answer('На данный момент каталог продуктов пуст, загляните к нам чуть позже')
        await callback.answer()

@router.callback_query(F.data.startswith('back'))
async def cmd_fast_food(callback: CallbackQuery):
    categ_id = int(callback.data.split('_')[-2])
    index = int(callback.data.split('_')[-1])
    print(index)
    item = await output_fast_food(categ_id)
    if item:
        if index > 0:
            index -= 1
            await callback.message.edit_media(media=InputMediaPhoto(media=item[index][1]))
            await callback.message.edit_caption(caption=f"<b><i>Наименование:</i></b> {item[index][0]}  \n\n<b><i>Описание продукта:</i></b> {item[index][2]}\n\n<b><i>Прайс:</i></b> {item[index][3]} BYN", reply_markup=await add_cart(categ_id, item[index][4], index))
            await callback.answer()
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=item[-1][1]))
            await callback.message.edit_caption(caption=f"<b><i>Наименование:</i></b> {item[-1][0]}  \n\n<b><i>Описание продукта:</i></b> {item[-1][2]}   \n\n<b><i>Прайс:</i></b> {item[-1][3]} BYN", reply_markup=await add_cart(categ_id, item[-1][4], len(item) - 1))
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

#@router.message(F.text.endswith('Корзина'))
#async def cmt_cart(message: Message):
#    cart_user = await chek_user_cart(message.from_user.id)
#    if cart_user:
#        for item in cart_user:
#            await message.answer_photo(item[1], caption=f"<b><i>Наименование:</i></b> {item[0]}\n\n<b><i>Описание продукта:</#i></b> {item[2]}\n\n<b><i>Прайс:</i></b> {item[3]} BYN", reply_markup=await bat_product_cart(item[4]))
#        await message.answer('Для подтверждения заказа нажмите ⬇️', reply_markup=order)
#    else:
#        await message.answer('Корзина пуста, перейдите в котолог [🍔 Еда] и сделайте свой выбор')

@router.message(F.text.endswith('Корзина'))
async def cmd_cart(message: Message):

    cart_user = await check_user_cart(message.from_user.id)
    print(cart_user)
    if cart_user:
        for item in cart_user:
            await message.answer(text=f'Позиция №{cart_user.index(item) + 1}', reply_markup=await user_cart_product(item[0]))
        await message.answer('Подтверждение заказа', reply_markup=confirmation_order)
    else:
        await message.answer('Корзина пуста, перейдите в котолог [🍔 Еда] и сделайте свой выбор')
        


@router.callback_query(F.data.endswith('minus'))
async def cmd_minus(callback: CallbackQuery):
    id_pr = int(callback.data.split()[0])
    if await minus_count_product(id_pr):
        await callback.message.edit_reply_markup(reply_markup=await update_in_bt(id_pr))
    else:
        await callback.answer('Минимальное количество 1 шт.')

@router.callback_query(F.data.endswith('plus'))
async def cmd_minus(callback: CallbackQuery):
    id_pr = int(callback.data.split()[0])
    if await plus_count_product(id_pr):
        await callback.message.edit_reply_markup(reply_markup=await update_in_bt(id_pr))
    else:
        await callback.answer('Максимальное количество 10 шт.')

@router.callback_query(F.data.endswith('count'))
async def cmd_minus(callback: CallbackQuery):
    check_count = await check_quantuty(int(callback.data.split()[0]))
    await callback.answer(f'У вас в корзине 🛒 {check_count} шт.')
    await callback.answer()



@router.callback_query(F.data.endswith('add_cart'))
async def cmd_add_cart(callback: CallbackQuery):
    id_categor = int(callback.data.split('_')[0])
    if await add_cart_product(callback.from_user.id, id_categor):
        await callback.answer(text='Товар добавлен в корзину')
    else:
        await callback.answer('Товар уже был добавлен в корзину', show_alert=True)


@router.callback_query(F.data.endswith('delete'))
async def delete_product(callback: CallbackQuery):
    if await delete_cart(callback.from_user.id, int(callback.data.split('_')[0])):
        await callback.answer(text='Товар удален')
        await callback.message.delete()
        await callback.message.delete_reply_markup()
    else:
        await callback.message.answer('Ошибка')
    

@router.callback_query(F.data == 'update')
async def update_cart_user(callback: CallbackQuery):
    cart_user = await check_user_cart(callback.from_user.id)
    if cart_user:
        for item in cart_user:
            await callback.message.answer_photo(item[1])
            await callback.message.answer(f"<b><i>Наименование:</i></b> {item[0]}\n\n<b><i>Описание продукта:</i></b> {item[2]}\n\n<b><i>Прайс:</i></b> {item[3]} BYN", reply_markup=await user_cart_product(item[4]))
        await callback.message.answer('Для подтверждения заказа нажмите ⬇️', reply_markup=order)
        await callback.answer()
    else:
        await callback.message.answer('Корзина пуста, перейдите в котолог [🍔 Еда] и сделайте свой выбор')
        await callback.answer()


@router.message(F.text.endswith('Помощь'))
async def cmd_help(message: Message):
    await message.answer('🔸У вас возникли вопросы?\nМы с удовольствием ответим!\n', reply_markup=kb_help)


@router.message()
async def cmd_echo(message: Message):
    await message.answer('Данная команда/текст находится в разработке или вы пишите какую-то ерунду и бот Вас не понимает 🥴')