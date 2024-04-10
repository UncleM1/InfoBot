from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def inline_kb_builder(*,btns:dict[str,str],size:tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    for text,data in btns.items():
        keyboard.add(
            InlineKeyboardButton(text=text,callback_data=data)
        )
    return keyboard.adjust(*size).as_markup()