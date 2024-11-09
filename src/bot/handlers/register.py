from aiogram import F, Router
from aiogram import types
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.bot.keyboards.inline import create_client_keyboard
from src.bot.loader import bot
from src.bot.schemas.register_schemas import RegProfile
from src.bot.states import Register
from src.db.repositories import UserDataRepository

register_router = Router()


@register_router.message(Command('cancel'))
async def cancel_registration(message: types.Message, state: FSMContext):
    logger.debug('Запущен процесс отмены.')
    state_getter = await state.get_state()
    logger.debug(f'{state_getter}, {type(state_getter)}')
    if state_getter is None:
        logger.debug('Нечего отменять.')
        await message.answer('Нечего отменять.')
        return
    if 'Register' in state_getter:
        logger.debug('Отменяю регистрацию...')
        user_data = await state.get_data()

        bot_msg = user_data.get('register_status')
        logger.debug(f'bot_msg: {bot_msg}')
        await bot_msg.edit_text(text='Процесс регистрации отменён.')

        last_msg = user_data.get('last_msg')
        if last_msg:
            await last_msg.delete()

        await state.clear()


@register_router.callback_query(F.data == 'register')
async def start_registration(message: types.CallbackQuery, state: FSMContext):
    if not await UserDataRepository().check_user(message.from_user.id):
        logger.debug('Принимаю ФИО...')
        bot_message = await bot.send_message(message.from_user.id, 'Пожалуйста, введите ваше ФИО:')
        await state.update_data(register_status=bot_message)
        await state.set_state(Register.full_name)
    else:
        await bot.send_message(message.from_user.id, 'Вы уже отправили заявку.')


@register_router.message(Register.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    logger.debug('Обрабатываю ФИО и принимаю номер телефона...')
    await message.delete()

    try:
        user_data = await state.get_data()
        last_msg = user_data.get('last_msg')
        if last_msg:
            await last_msg.delete()

        RegProfile(full_name=message.text)
    except ValueError as ex:
        logger.error(ex)
        logger.error(f'Неправильное ФИО! (Введено: {message.text})')
        answer = await message.answer(f'Неправильное ФИО, введите заново (Введено: {message.text}):')
        await state.update_data(last_msg=answer)
        return

    await state.update_data(full_name=message.text)

    bot_msg = user_data.get('register_status')
    await bot_msg.edit_text(text='\n'.join([
        '<b>ПРОЦЕСС РЕГИСТРАЦИИ</b>\n',
        f'ФИО: {message.text}',
        '\n/cancel - для отмены'
    ]), parse_mode=ParseMode.HTML)

    answer = await message.answer('Введите номер телефона:')
    await state.update_data(last_msg=answer)
    await state.set_state(Register.phone_number)


@register_router.message(Register.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    logger.debug('Обрабатываю номер телефона и беру тип клиента...')
    await message.delete()

    try:
        user_data = await state.get_data()
        last_msg = user_data.get('last_msg')
        if last_msg:
            await last_msg.delete()

        RegProfile(phone_number=message.text)
    except ValueError:
        logger.error(f'Неправильный номер телефона! (Введено: {message.text})')
        answer = await message.answer(f'Неправильный номер телефона, введите заново (Введено: {message.text}):')
        await state.update_data(last_msg=answer)
        return

    await state.update_data(phone_number=message.text)

    bot_msg = user_data.get('register_status')
    await bot_msg.edit_text(text='\n'.join([
        '<b>ПРОЦЕСС РЕГИСТРАЦИИ</b>\n',
        f'ФИО: {user_data.get("full_name")}',
        f'Телефон: {message.text}',
        '\n/cancel - для отмены'
    ]), parse_mode=ParseMode.HTML)

    answer = await message.answer('К какой категории вы относитесь?', reply_markup=create_client_keyboard())
    await state.update_data(last_msg=answer)
    await state.set_state(Register.client_type)


@register_router.callback_query(F.data == 'Частное лицо', Register.client_type)
@register_router.callback_query(F.data == 'Организация', Register.client_type)
@register_router.callback_query(F.data == 'Собственник', Register.client_type)
async def process_client_type(message: types.CallbackQuery, state: FSMContext):
    logger.debug('Обрабатываю тип клиента и потенциально запрашиваю имя организации...')

    user_data = await state.get_data()
    last_msg = user_data.get('last_msg')
    if last_msg:
        await last_msg.delete()
    RegProfile(client_type=message.data)

    await state.update_data(client_type=message.data)

    if message.data == 'Организация':
        bot_msg = user_data.get('register_status')
        await bot_msg.edit_text(text='\n'.join([
            '<b>ПРОЦЕСС РЕГИСТРАЦИИ</b>\n',
            f'ФИО: {user_data.get("full_name")}',
            f'Телефон: {user_data.get("phone_number")}',
            f'Категория: {message.data}',
            '\n/cancel - для отмены'
        ]), parse_mode=ParseMode.HTML)

        answer = await bot.send_message(message.message.chat.id, 'Введите имя организации:')
        await state.update_data(last_msg=answer)

        await state.set_state(Register.organization_name)
    else:
        bot_msg = user_data.get('register_status')
        db_info = RegProfile(
            tg_id=message.from_user.id,
            full_name=user_data.get("full_name"),
            phone_number=user_data.get("phone_number"),
            client_type=message.data
        )
        await bot_msg.edit_text(text='\n'.join([
            '<b>РЕГИСТРАЦИЯ ЗАВЕРШЕНА</b>\n',
            'Ваша заявка находится на рассмотрении',
            f'ФИО: {db_info.full_name}',
            f'Телефон: {db_info.phone_number}',
            f'Категория: {message.data}'
        ]), parse_mode=ParseMode.HTML)

        db_status = await UserDataRepository().add_data(db_info)
        logger.info(f'Новая анкета: {db_status}')
        await state.clear()


@register_router.message(Register.organization_name)
async def process_organization_name(message: types.Message, state: FSMContext):
    logger.debug('Обрабатываю имя организации...')
    await message.delete()

    try:
        user_data = await state.get_data()
        last_msg = user_data.get('last_msg')
        if last_msg:
            await last_msg.delete()

        RegProfile(organization_name=message.text)
    except ValueError:
        logger.error(f'Неправильное имя организации! (Введено: {message.text})')
        answer = await message.answer(f'Неправильное имя организации, введите заново (Введено: {message.text}):')
        await state.update_data(last_msg=answer)
        return

    await state.update_data(organization_name=message.text)

    bot_msg = user_data.get('register_status')
    db_info = RegProfile(
        tg_id=message.from_user.id,
        full_name=user_data.get("full_name"),
        phone_number=user_data.get("phone_number"),
        client_type=user_data.get("client_type"),
        organization_name=message.text
    )
    await bot_msg.edit_text(text='\n'.join([
        '<b>РЕГИСТРАЦИЯ ЗАВЕРШЕНА</b>\n',
        'Ваша заявка находится на рассмотрении',
        f'ФИО: {user_data.get("full_name")}',
        f'Телефон: {user_data.get("phone_number")}',
        f'Категория: {user_data.get("client_type")}',
        f'Имя организации: {message.text}'
    ]), parse_mode=ParseMode.HTML)
    db_status = await UserDataRepository().add_data(db_info)
    logger.info(f'Новая анкета: {db_status}')
    await state.clear()
