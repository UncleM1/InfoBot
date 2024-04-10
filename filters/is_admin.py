from aiogram.filters import Filter
from aiogram import types, Bot


class IsAdminFilter(Filter):
    def __init__(self):
        pass

    async def __call__(self, message: types.Message, bot: Bot):
        return message.from_user.id in bot.my_admins_list
