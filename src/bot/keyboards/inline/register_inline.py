from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_reg_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text='Заполнить анкету',
                callback_data='register'
            )
        ]]
    )
    return keyboard
