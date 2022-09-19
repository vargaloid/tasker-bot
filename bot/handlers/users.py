from loguru import logger
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import debug_mode
from bot.handlers.database import add_user, del_user, get_users


class UserManagement(StatesGroup):
    waiting_add_or_del = State()
    waiting_forwarded_message = State()
    waiting_user_to_del = State()


async def callback_add_user(callback_query: types.CallbackQuery):
    logger.info(f'Command: <user> - Callback Query - <{callback_query.data}>')
    if debug_mode:
        logger.debug(f'Command: <user> - Callback Query - <{callback_query}>')
    await callback_query.message.edit_text(text='To add - forward to me any message from the user you want to add')
    await UserManagement.waiting_forwarded_message.set()


async def callback_del_user(callback_query: types.CallbackQuery):
    logger.info(f'Command: <user> - Callback Query - <{callback_query.data}>')
    if debug_mode:
        logger.debug(f'Command: <user> - Callback Query - <{callback_query}>')
    users = get_users()
    msg = "<b>Users list:</b>"
    for user in users:
        msg_user = ' '.join(filter(None, (str(user.telegram_id), '-',
                                          user.telegram_first_name, user.telegram_last_name,
                                          user.telegram_username)))
        msg = msg + '\n' + msg_user
    msg = msg + '\n\nWhich user you want to delete (provide ID)?'
    await callback_query.message.edit_text(msg)
    await UserManagement.waiting_user_to_del.set()


async def forwarded_message_add_user(message: types.Message, state: FSMContext):
    logger.info(f'Command: <user> - Forwarded message to add user - <{message.forward_from}>')
    if debug_mode:
        logger.debug(f'Command: <user> - Forwarded message to add user - <{message}>')
    # Telegram user can have forward message privacy
    if message.forward_from:
        adding_status = add_user(message)
        if adding_status[1]:
            await message.answer("User successfully added!🤝\n\n"
                                 f"ID: <b>{message.forward_from.id}</b>\n"
                                 f"Username: <b>{message.forward_from.username}</b>\n"
                                 f"First name: <b>{message.forward_from.first_name}</b>\n"
                                 f"Last name: <b>{message.forward_from.last_name}</b>\n")
        else:
            await message.answer("User already exists!🤦‍♂️")
    else:
        await message.answer("User has forward message privacy. 🤷‍♂️ Please, add user manually.")
    await state.finish()


async def id_del_user(message: types.Message, state: FSMContext):
    logger.info(f'Command: <user> - Message to del user - <{message.text}>')
    if debug_mode:
        logger.debug(f'Command: <user> - Message to del user - <{message}>')
    del_status = del_user(message.text)
    # there may be no such user
    if del_status is None:
        await message.answer("There is no user with such telegram ID 🤷‍♂️")
    else:
        await message.answer("User successfully deleted!💀")
    await state.finish()


def register_users(dp: Dispatcher):
    dp.register_callback_query_handler(callback_add_user, lambda c: c.data == 'add_user',
                                       state=UserManagement.waiting_add_or_del, is_user=True)
    dp.register_callback_query_handler(callback_del_user, lambda c: c.data == 'del_user',
                                       state=UserManagement.waiting_add_or_del, is_user=True)
    dp.register_message_handler(forwarded_message_add_user, content_types=["text", "sticker"],
                                state=UserManagement.waiting_forwarded_message, is_user=True)
    dp.register_message_handler(id_del_user,
                                state=UserManagement.waiting_user_to_del, is_user=True)
