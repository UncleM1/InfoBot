from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import async_session

from DataBase.models import Product,Customer


#ORM querie for Product

async def orm_add_product(session:async_session,data:dict):

    obj = Product(
        name = data["name"],
        description = data["description"],
        price =float(data["price"])
    )

    session.add(obj)
    await session.commit()



async def orm_get_products(session:async_session):
    querie = select(Product)
    result = await session.execute(querie)
    return result.scalars().all()



async def orm_get_product(session:async_session,product_id:int):
    querie = select(Product).where(Product.id==product_id)
    result = await session.execute(querie)
    return result.scalar()



async def orm_update_product(session:async_session,product_id:int,data:dict):
    querie = update(Product).where(Product.id==product_id).values(
        name = data["name"],
        description = data["description"],
        price = data["price"]
    )
    await session.execute(querie)
    await session.commit()



async def orm_delete_product(session:async_session,product_id:int):
    querie = delete(Product).where(Product.id==product_id)
    await session.execute(querie)
    await session.commit()



#ORM querie for Customer

async def orm_add_customer(session: async_session, data: dict):
    cstm = Customer(
        user_id=data["user_id"],
        first_name=data["first_name"],
        # phone_number=data["phone_number"],
    )

    session.add(cstm)
    await session.commit()


async def orm_update_customer(session: async_session, data: dict, customer_id:int):

    querie = update(Customer).where(Customer.user_id == customer_id).values(
        phone_number = data["phone_number"]
    )

    await session.execute(querie)
    await session.commit()


async def orm_get_customers(session:async_session):
    querie = select(Customer)
    result = await session.execute(querie)
    return result.scalars().all()


async def orm_get_customers_id(session:async_session):
    querie = select(Customer.user_id)
    result = await session.execute(querie)
    return result.scalars().all()


async def orm_get_customer(session:async_session,customer_id:int):
    querie = select(Customer).where(Customer.user_id==customer_id)
    result = await session.execute(querie)
    return result.scalars()


async def orm_customer_phone(session:async_session,customer_id:int):
    querie = select(Customer.phone_number).where(Customer.user_id==customer_id)
    result = await session.execute(querie)
    return result.scalars().all()
