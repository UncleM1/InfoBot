from string import punctuation

from aiogram import Router, types, Bot, F
from aiogram.filters import Command

from filters.chat_type import ChatTypeFilter

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(["group","supergroup"]))

restricted_words = {"хуй", "пизда", "еблан", "ебать","пиздец", }

# def cleaner(text:str):
#     return text.translate(str.maketrans("", "", punctuation))


@user_group_router.message(Command("admin"))
async def get_admins(message:types.Message,bot=Bot):
    supergroup_id = message.chat.id
    admins_list =await bot.get_chat_administrators(chat_id=supergroup_id)
    admins_list = [
        member.user.id
        for member in admins_list
        if member.status == "creator" or member.status == "administrator"
    ]
    bot.my_admins_list = admins_list
    if message.from_user.id in admins_list:
        await message.delete()

@user_group_router.edited_message()
@user_group_router.message()
async def group_message_control(message:types.Message):
    try:
        if restricted_words.intersection(message.text.lower().split()):
            await message.answer(f"{message.from_user.first_name},соблюдай порядок в чате!")
            await message.delete()
    except:
        await message.answer("What is the strange message...")


