import os

from aiogram import Router,types,Bot
from aiogram.filters import Command, or_f, StateFilter
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import async_session

from ORM.ORM_Query import orm_add_product, orm_get_product, orm_get_products,orm_delete_product, orm_update_product, orm_get_customers
from keyboards.reply import admin_kb,start_kb
from keyboards.inline import inline_kb_builder
from filters.chat_type import ChatTypeFilter
from filters.is_admin import IsAdminFilter
from dotenv import load_dotenv, find_dotenv

admin_router = Router()
admin_router.message.filter(IsAdminFilter())
admin_router.message.filter(ChatTypeFilter(["private"]),)

load_dotenv(find_dotenv())


class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()

    product_for_change = None




@admin_router.message(F.text.lower() == "admin")
async def admin_start(message:types.Message):
    await message.answer("Что вы хотели, Boss?",reply_markup=admin_kb)


@admin_router.message(F.text.lower() == "назад")
async def Back(message:types.Message):
    await message.answer("Ok,Boss",reply_markup=start_kb)



@admin_router.message(F.text.lower() == "справка")
async def Back(message:types.Message):
    await message.answer("Все что вам нужно знать об админ панели - эта штука максимально проста.\n\n"
                         "Если вы хотите добавить товар или сделать рассылку вам достаточно следовать инструкция на экране.\n\n"
                         "Если вы ввели некорректные данные, вы хотите вернуться к стартовому состоянию или вы просто передумали - напишите в стороке ввода  отмена.\n\n"
                         "Если вы захотели вернуться к пользовательской клавиатуре воспользуйтесь кнопкой Back.\n\n"
                         "Если случилось что то непонятное и ваша панель админа пересиала реагировать просто введите комманду /start\n\n")





@admin_router.message(F.text.lower() == "продукты")
async def My_Products(message:types.Message,session:async_session):
    for product in await orm_get_products(session):
        await message.answer(f"{product.name}\n{product.description}\nPrice:{round(product.price,2)}$",
            reply_markup=inline_kb_builder(
            btns={
                "Удалить":f"delete_{product.id}",
                "Изменить":f"change_{product.id}"
                  }
            )
                )


@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_product(callback:types.CallbackQuery, session:async_session,):
    product_id = callback.data.split("_")[-1]
    await orm_delete_product(session, int(product_id))
    await callback.answer("Продукт удален",show_alert=True)
    await callback.message.delete()



@admin_router.callback_query(StateFilter(None),F.data.startswith("change_"))
async def change_product(callback:types.CallbackQuery, state:FSMContext, session:async_session,):
    product_id = callback.data.split("_")[-1]

    product_for_change = await orm_get_product(session,product_id)
    AddProduct.product_for_change = product_for_change

    await callback.answer()
    await callback.message.answer("Введите название товара", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddProduct.name)



#FSM Add product



@admin_router.message(StateFilter(None), F.text.lower() == "добавить товар")
async def Addproduct(message:types.Message,state:FSMContext):
    await message.answer("Введите название продукта",reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddProduct.name)



@admin_router.message(AddProduct.name, or_f(F.text, F.text=="."))
async def Addproduct_name(message:types.Message,state:FSMContext):

    if message.text == ".":
        await state.update_data(name = AddProduct.product_for_change.name)
    else:
        await state.update_data(name = message.text)

    await message.answer("Введите описание продукта")
    await state.set_state(AddProduct.description)

@admin_router.message(AddProduct.name)
async def Addproduct_name(message:types.Message,state:FSMContext):
    await message.answer("Вы ввели некорректные данные\nПожалуйста, введите текстовое название товара")



@admin_router.message(AddProduct.description, or_f(F.text, F.text=="."))
async def Addproduct_description(message:types.Message,state:FSMContext):
    if message.text == ".":
        await state.update_data(description = AddProduct.product_for_change.description)
    else:
        await state.update_data(description = message.text)

    await message.answer("Введите стоимость продукта")
    await state.set_state(AddProduct.price)

@admin_router.message(AddProduct.description)
async def Addproduct_description(message:types.Message):
    await message.answer("Вы ввели некорректные данные\nПожалуйста, введите текстовое описание товара")




@admin_router.message(AddProduct.price, or_f(F.text, F.text=="."))
async def Addproduct_price(message:types.Message,state:FSMContext, session:async_session):
    if message.text ==".":
        await state.update_data(price = AddProduct.product_for_change.price)
    else:
        await state.update_data(price = message.text)

    data = await state.get_data()
    try:
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
            AddProduct.product_for_change = None
        else:
            await orm_add_product(session,data)

        await message.answer("Продукт добавлен",reply_markup=admin_kb)
        await state.clear()

    except Exception as e:
        await message.answer(f"Ошибка{e}.Спросите у вашего программиста. Он опять денег хочет...",reply_markup=admin_kb)
        await state.clear()



@admin_router.message(AddProduct.price)
async def Addproduct_price(message: types.Message):
    await message.answer("Вы ввели некорректные данные\nПожалуйста, введите зчисловое значение цены продукта")



#FSM make mailling

class Mailling(StatesGroup):
    text = State()

@admin_router.message(StateFilter(None), F.text.lower() == "создать рассылку")
async def make_mailling (message:types.Message,state:FSMContext):
    await message.answer("Введите сообщение здесь",reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Mailling.text)



@admin_router.message(Mailling.text, F.text.lower()!="отмена")
async def send_malling(message:types.Message,state:FSMContext, session:async_session, bot:Bot):
    await state.update_data(text = message.text)

    supergroup_id = os.getenv("supergroup_id")
    data = await state.get_data()
    blocked_counter = 0

    for cstmr in await orm_get_customers(session):
        try:
            await bot.send_message(chat_id=cstmr.user_id,text=f"Hi, {cstmr.first_name}!\n{data['text']}",
                                   reply_markup=inline_kb_builder(
                                     btns={
                                         "Хочу": f"want_{supergroup_id}"
                                        }
                                                                )
                                )

        except Exception as e:
            blocked_counter+=1

    await message.answer(f"Рассылка успешно отправлена!\n{blocked_counter} пользователей нас заблокировало(((", reply_markup=admin_kb)
    await state.clear()




#FSM Reset state

@admin_router.message(StateFilter("*"),F.text.lower() == "отмена")
async def reset_state(message:types.Message,state:FSMContext):

    curent_state = await state.get_state()
    if curent_state is None:
        await message.answer("U don't enter anything, Billy the Kid =)")
        return

    await state.clear()
    await message.answer("Ok. Ваше состояние вернулось в стартовое",reply_markup=admin_kb)









