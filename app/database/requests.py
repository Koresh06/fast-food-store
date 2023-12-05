from app.database.models import async_session
from app.database.models import User, Cart, CartItem, Product, Categories, Orders
from sqlalchemy import select, update, delete


async def chek_user(tg_id, username):
    async with async_session() as session:
        user_query = await session.scalar(select(User).where(User.tg_id == tg_id, User.username == username))
        if not user_query:
            return False
        
        return True
    
async def add_user(tg_id, username):
    async with async_session() as session:
        try:
            session.add(User(tg_id=tg_id, username=username))
            session.add(Cart(user_id=tg_id))
            await session.commit()
            return True
        except Exception() as exxit:
            print(exxit)
            return False
        
async def output_categories():
    async with async_session() as session:
        name_cat = await session.execute(select(Categories.name, Categories.id))
    return name_cat

async def add_categories(name_cat):
    async with async_session() as session:
        name_d = await session.scalar(select(Categories).where(Categories.name == name_cat))
        if not name_d:
            session.add(Categories(name=name_cat))
            await session.commit()
            return True
        else:
            return False


async def add_product_db(tg_id, product: dict):
    async with async_session() as session:
        try:
            user_d = await session.scalar(select(User).where(User.tg_id == tg_id))
            session.add(Product(user_id=user_d.id, categories_id=product['id_categ'], name=product['name'],   image=product['image'], description=product   ['description'], price=product['price']))
            count = await session.scalar(select(Categories.count).where(Categories.id == product['id_categ']))
            count += 1
            await session.execute(update(Categories).where(Categories.id == product['id_categ']).values(count=count))
            await session.commit()
            return True
        except:
            return False
        
async def output_fast_food(id_categ) -> list:
    async with async_session() as session:
        fast_food = await session.execute(select(Product.name, Product.image, Product.description, Product.price, Product.id).where(Product.categories_id == id_categ))
        if fast_food:
            return fast_food.all()
        return False
   

async def add_cart_product(tg_id, id_categ):
    async with async_session() as session:
        cart_user = await session.scalar(select(Cart).where(Cart.user_id == tg_id))
        product_item = await session.scalar(select(Product).where(Product.id == int(id_categ)))
        check_cartitem = await session.scalar(select(CartItem).where(CartItem.cart_id == cart_user.id, CartItem.product_id == product_item.id))
        if not check_cartitem:
            session.add(CartItem(cart_id=cart_user.id, product_id=product_item.id))
            await session.commit()
            return True
        else: 
            return False


async def check_user_cart(tg_id):
    async with async_session() as session:
        user_d = await session.scalar(select(Cart).where(Cart.user_id == tg_id))
        product_d = await session.execute(select(CartItem.product_id).where(Cart.id == user_d.id))
        if product_d:
            return product_d.all()
        return False
    
async def pars_product(id_pr):
    async with async_session() as session:
        attr_pr = await session.execute(select(Product.name, Product.price).where(Product.id == id_pr))
        count = await session.scalar(select(CartItem.quantuty).where(CartItem.product_id == id_pr))
        return *attr_pr.all(), count

async def inline_kb_product(id_product):
    async with async_session() as session:
        product_d = await session.execute(select(Product.name).where(Product.id == id_product))
        if product_d:
            return product_d.all()
        return False
        

async def count_quantuty(categ_id):
    async with async_session() as session:
        count = await session.scalar(select(Categories.count).where(Categories.id == categ_id))
    return count


async def delete_cart(tg_id, data):
    async with async_session() as session:
        try:
            user_d = await session.scalar(select(Cart).where(Cart.user_id == tg_id))
            product_item = await session.scalar(select(Product).where(Product.id == data))
            del_item_cart = await session.scalar(select(CartItem).where(CartItem.cart_id == user_d.id, CartItem.product_id == product_item.id))
            await session.delete(del_item_cart)
            await session.commit()
            return True
        except: 
            return False

async def count_minus(name):
    async with async_session() as session:
        name_d = await session.scalar(select(Product).where(Product.name == name.strip()))
        count = await session.scalar(select(CartItem.quantuty).where(CartItem.product_id == name_d.id))
        if count > 1:
            count -= 1
            await session.execute(update(CartItem).where(CartItem.product_id == name_d.id).values(quantuty=count))
            await session.commit()
            return True
        return False
    
async def clear_cart_pr(tg_id):
    async with async_session() as session:
        #try:
            user_d = await session.scalar(select(Cart).where(Cart.user_id == tg_id))
            clear_d = await session.scalars(select(CartItem).where(CartItem.cart_id == user_d.id))
            for clear in clear_d:
                await session.delete(clear)
            await session.commit()
            return True
        #except:
            #return False



async def delete_menu_product(name):
    async with async_session() as session:
        try:
            name_d = await session.scalar(select(Product).where(Product.name == name.strip()))
            del_pr = await session.scalar(select(CartItem).where(CartItem.product_id == name_d.id))
            await session.delete(del_pr)
            await session.commit()
            return True
        except:
            return False


async def check_quantuty(id_product):
    async with async_session() as session:
        quantuty = await session.scalar(select(CartItem.quantuty).where(CartItem.product_id == id_product))
    return quantuty

async def minus_count_product(id_product):
    async with async_session() as session:
        count = await session.scalar(select(CartItem.quantuty).where(CartItem.product_id == id_product))
        print(count)
        if count > 1:
            count -= 1
            await session.execute(update(CartItem).where(CartItem.product_id == id_product).values(quantuty=count))
            await session.commit()
            return True
        return False
    
async def plus_count_product(id_product):
    async with async_session() as session:
        count = await session.scalar(select(CartItem.quantuty).where(CartItem.product_id == id_product))
        if count < 10:
            count += 1
            await session.execute(update(CartItem).where(CartItem.product_id == id_product).values(quantuty=count))
            await session.commit()
            return True
        return False
    
#Сбор id_product и количества товара для оплаты
async def payment_cart(tg_id):
    async with async_session() as session:
        try:
            cart_d = await session.scalar(select(Cart).where(Cart.user_id == tg_id))
            cartitem_d = await session.execute(select(CartItem.product_id, CartItem.quantuty).where(CartItem.cart_id == cart_d.id))
            return cartitem_d.all()
        except Exception() as exxit:
            print(exxit)
            return False

#Название, описание и прайс
async def product_name_desc_price(id_pord):
    async with async_session() as session:
        product_d = await session.execute(select(Product.name, Product.price).where(Product.id == id_pord))
    return product_d.all()

#Оплата при получениия
async def save_order(tg_id: int, address: str, content: dict):
    async with async_session() as session:
        user_d = await session.scalar(select(User).where(User.tg_id == tg_id))
        cart_d = await session.scalar(select(Cart).where(Cart.user_id == tg_id))
        session.add(Orders(user_id=user_d.id, cart_id=cart_d.id, address=address, order=content))
        await session.commit()

#Подтверждение оплаты с карты
async def payment_confirmation(tg_id, id_):
    async with async_session() as session:
        await session.execute(update(Orders).where(Orders.id == id_).values(payment=1))
        await session.commit()

#Послдений товар оплаченный картой
async def tovar_last(tg_id):
    async with async_session() as session:
        user_d = await session.scalar(select(User).where(User.tg_id == tg_id))
        cart_d = await session.scalar(select(Cart).where(Cart.user_id == tg_id))
        content = await session.execute(select(Orders.id).where(Orders.user_id == user_d.id, Orders.cart_id == cart_d.id))
        if content:
            return content.all()
        return False
    
#Получение списка пользователей
async def users():
    async with async_session() as session:
        users_d = await session.execute(select(User.username, User.tg_id))
        if users_d:
            return users_d.all()
        return False


