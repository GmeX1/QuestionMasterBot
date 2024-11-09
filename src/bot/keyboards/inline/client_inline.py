from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_client_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Частное лицо',
                callback_data='Частное лицо'
            )],
            [InlineKeyboardButton(
                text='Организация',
                callback_data='Организация'
            )],
            [InlineKeyboardButton(
                text='Собственник',
                callback_data='Собственник'
            )]
        ]
    )
    return keyboard
