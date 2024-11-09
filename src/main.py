import asyncio

from loguru import logger
import sys
from bot.loader import dp, bot
from bot.handlers import routers
from db import init_models
logger.remove()
# logger.add(sys.stderr, level='DEBUG', enqueue=True, colorize=True)
# Раньше надо было ставить отдельно выходы в файл и в поток, но в последних обновлениях, кажется, что-то поменяли
logger.add('debug_log.log', level='DEBUG', enqueue=True, retention=2, rotation='3 days')


dp.include_routers(*routers)


async def main():
    try:
        logger.info('Запускаю бд...')
        await init_models()
        logger.info('Запускаю бота...')
        await dp.start_polling(bot)
    except Exception as ex:
        logger.error(f'Ошибка при выполнении: {ex}')


if __name__ == '__main__':
    logger.add(sys.stderr, level='DEBUG', enqueue=True, colorize=True)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Останавливаю работу...')
