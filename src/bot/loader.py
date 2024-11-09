# from bot.handlers import routers
from aiogram import Bot, Dispatcher
from src.utils.load_env import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

