from aiogram import types, Router
from aiogram.filters import Command
from src.bot.keyboards.inline import create_reg_keyboard

start_router = Router()


@start_router.message(Command('start'))
async def start_command(message: types.Message):
    await message.answer('Добро пожаловать!\nЧтобы отправить свои данные, нажмите "Заполнить анкету"',
                         reply_markup=create_reg_keyboard())
