import os

from aiogram import Router, types, Bot
from aiogram.filters import CommandStart, Command, or_f
from aiogram import F
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import async_session

from ORM.ORM_Query import orm_get_products, orm_get_customers_id, orm_add_customer, orm_get_customer,orm_customer_phone, orm_update_customer
from filters.chat_type import ChatTypeFilter
from handlers.user_group import user_group_router
from keyboards.inline import inline_kb_builder
from keyboards.reply import start_kb, send_phone_kb


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))

load_dotenv(find_dotenv())

supergroup_id = os.getenv("supergroup_id")

@user_private_router.message(CommandStart())
async def start_command(message:types.message, session:async_session):

    if message.from_user.id not in await orm_get_customers_id(session):
        data = {
            "first_name": message.from_user.first_name,
            "user_id": message.from_user.id,
        }
        await orm_add_customer(session, data)

    await message.answer("Привет!👋\nМеня зовут Bot SID."
                         " Я помогаю узнать кто мы такие, ознакомиться с нашими продуктами,"
                         " а еще я отвечвю на часто задаваемые вопросы\n"
                         "Так же прямо здесь вы можете оформить заявку и наш менеджер свяжется с вами в ближайшее время\n"
                         "Начнем ?)...🚀",
                         reply_markup=start_kb)

@user_private_router.message(or_f((Command("about")),(F.text.lower() == "о нас")))
async def about_us(message:types.Message):
    await message.answer("SID это IT сообщество, которое помогает салонам, магазинам"
                         " и, в общем, всем , кто хотел бы автоматизировать бизнес процессы,"
                         " освободить руки от рутинных задач и, самое главное, продвигать свой бизнес в мессенжерах.\n"
                         "Присоединяйтесь и выходите на новый уровень вместе с нами 🤝")

@user_private_router.message(or_f((Command("products")),(F.text.lower() == "наши продукты")))
async def our_products(message:types.Message,session:async_session):
        for product in await orm_get_products(session):
            await message.answer(f"{product.name}\n{product.description}\nPrice:{round(product.price,2)}$")


@user_private_router.message(or_f((Command("FAQ")),(F.text.lower() == "faq")))
async def our_products(message:types.Message):
        await message.answer("Я еще только учусь и вопросов мне еще не задавли)\n"
                             "Обещаю в будущем стать умнее и больше вам помогать🥺")





@user_private_router.message(or_f((Command("request")),(F.text.lower() == "оставить заявку")))
async def request(message:types.Message,session:async_session):

    await message.answer("Оставьте заявку и мы свяжемся с вами!\n"
                         "Уточним детали и подробнее расскажем о наших продукиах",
                     reply_markup=inline_kb_builder(
                         btns={
                             "Оставить заявку": f"request_{supergroup_id}"
                         }
                     )
                     )



@user_private_router.callback_query(F.data.startswith("request_"))
async def send_request(callback:types.CallbackQuery,session:async_session,bot:Bot):
    try:
        for cstmr in await orm_get_customer(session, callback.from_user.id):
            if await orm_customer_phone(session, callback.from_user.id) != [None]:
                await callback.answer("Заявка отпралена", show_alert=True)
                await bot.send_message(text=f"{cstmr.first_name} с номером телефона {cstmr.phone_number} \n"
                                            f"и телеграм id = {cstmr.user_id} оставил заявку! \nНе забудь перезвонить!",
                                       chat_id=callback.data.split("_")[-1]
                                       )
            else:
                await callback.message.answer("Нам необходим ваш номер телефона", reply_markup=send_phone_kb)

    except:
        await bot.send_message(text="У пользователей что то не так с кнопкой заявки",chat_id=supergroup_id)



@user_private_router.callback_query(F.data.startswith("want_"))
async def inline_from_mailling(callback: types.CallbackQuery, session: async_session, bot: Bot):
    try:
        for cstmr in await orm_get_customer(session, callback.from_user.id):
            if await orm_customer_phone(session, callback.from_user.id) != [None]:
                await callback.answer("Заявка отпралена", show_alert=True)
                await bot.send_message( text=f"{cstmr.first_name} с номером телефона {cstmr.phone_number} \n"
                                        f"и телеграм id = {cstmr.user_id} оставил заявку! \nНе забудь перезвонить!",
                                        chat_id=callback.data.split("_")[-1]
                                       )
            else:
                await callback.message.answer("Нам необходим ваш номер телефона", reply_markup=send_phone_kb)

    except:
        await bot.send_message(text="У пользователей что то не так с кнопкой заявки", chat_id=supergroup_id)



@user_private_router.message(F.contact)
async def give_phone(message:types.Message,session: async_session):
    data = {
        "phone_number" : message.contact.phone_number
    }
    await orm_update_customer(session=session,data=data,customer_id=message.from_user.id)
    await message.answer("Данные успешно отправлены \n"
                         "Попробуйте снова отправить заявку",reply_markup=start_kb)


@user_private_router.message(F.text.lower() == "мне нужно еще подумать")
async def dont_give_phone(message:types.Message):
    await message.answer("Ok\nБудем ждать вас =)",reply_markup=start_kb)







