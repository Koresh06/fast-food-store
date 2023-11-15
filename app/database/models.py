from sqlalchemy import ForeignKey, String, BigInteger, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from typing import List
import config


engine = create_async_engine(
    url=config.SQLALCHEMY_URL,
    echo=config.SQLALCHEMY_ECHO
)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String())
    first_name: Mapped[str] = mapped_column(String(), default=None)
    last_name: Mapped[str] = mapped_column(String(), default=None)
    phone_number: Mapped[str] = mapped_column(String(), default=None)

    cart_user: Mapped[List['Cart']] = relationship(back_populates='user_rel', cascade='all, delete')

class Categories(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String())
    count: Mapped[int] = mapped_column(Integer(), default=0)

    product_rel: Mapped[List['Product']] = relationship(back_populates='categories_rel', cascade='all, delete')   

class Product(Base):
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    categories_id: Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String())
    image: Mapped[str] = mapped_column(String())
    description: Mapped[str] = mapped_column(String())
    price: Mapped[float] = mapped_column(Float())

    cartitem_rel: Mapped[List['CartItem']] = relationship(back_populates='product_rel', cascade='all, delete')
    categories_rel: Mapped['Categories'] = relationship(back_populates='product_rel')

class Cart(Base):
    __tablename__ = 'cart'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))

    user_rel: Mapped['User'] = relationship(back_populates='cart_user')
    items: Mapped[List['CartItem']] = relationship(back_populates='cart_rel', cascade='all, delete')

class CartItem(Base):
    __tablename__ = 'cartitem'

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey('cart.id', ondelete='CASCADE'))
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id', ondelete='CASCADE'))
    quantuty: Mapped[int] = mapped_column(default=1)

    cart_rel: Mapped['Cart'] = relationship(back_populates='items')
    product_rel: Mapped['Product'] = relationship(back_populates='cartitem_rel')


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)