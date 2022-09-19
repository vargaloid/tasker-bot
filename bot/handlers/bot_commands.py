from loguru import logger
from aiogram import types, Dispatcher

from config import debug_mode
from bot.keyboards.inline import inline_kb_users
from bot.handlers.users import UserManagement
from bot.handlers.tasks import TaskManagement
from bot.handlers.database import get_users, get_tasks


async def cmd_start(message: types.Message):
    logger.info(f'Command: <start> - {message.from_user.username}:{message.from_user.id}')
    if debug_mode:
        logger.debug(f'Command: <start> - <{message}>')
    await message.answer(f"Hello {message.from_user.username}")


async def cmd_version(message: types.Message):
    logger.info(f'Command: <version> - {message.from_user.username}:{message.from_user.id}')
    await message.answer("Bot version: <b>0.1.2</b>")


async def cmd_id(message: types.Message):
    logger.info(f'Command: <ID> - {message.from_user.username}:{message.from_user.id}')
    if debug_mode:
        logger.debug(f'Command: <ID> - {message}')
    await message.answer(f"Your ID: <b>{message.from_user.id}</b>")


async def cmd_user(message: types.Message):
    logger.info(f'Command: <user> - {message.from_user.username}:{message.from_user.id}')
    users = get_users()
    msg = "<b>Users list:</b>"
    for user in users:
        msg_user = ' '.join(filter(None, (str(user.telegram_id), '-',
                                          user.telegram_first_name, user.telegram_last_name,
                                          user.telegram_username)))
        msg = msg + '\n' + msg_user
    await message.answer(msg, reply_markup=inline_kb_users)
    await UserManagement.waiting_add_or_del.set()


async def cmd_task(message: types.Message):
    logger.info(f'Command: <task> - {message.from_user.username}:{message.from_user.id}')
    if debug_mode:
        logger.debug(f'Command: <task> - {message}')
    user_tasks = get_tasks(message.from_user.id)
    msg = "<b>Tasks list:</b>\n\n"
    for task in user_tasks:
        author = ' '.join(filter(None, (task.user.telegram_first_name, task.user.telegram_last_name)))
        msg_task = f"<b>Name:</b> {task.name}\n"\
                   f"<b>Description:</b> {task.description}\n"\
                   f"<b>Author:</b> {author}\n\n"
        msg = msg + msg_task
    await message.answer(msg)


async def cmd_task_all(message: types.Message):
    logger.info(f'Command: <task> - {message.from_user.username}:{message.from_user.id}')
    if debug_mode:
        logger.debug(f'Command: <task> - {message}')
    users = get_users()
    for user in users:
        user_tasks = get_tasks(user.telegram_id)
        assigned = ' '.join(filter(None, (user.telegram_first_name, user.telegram_last_name)))
        msg = f"<b>{assigned} Tasks list:</b>\n\n"
        for task in user_tasks:
            author = ' '.join(filter(None, (task.user.telegram_first_name, task.user.telegram_last_name)))
            msg_task = f"<b>Name:</b> {task.name}\n"\
                       f"<b>Description:</b> {task.description}\n"\
                       f"<b>Author:</b> {author}\n\n"
            msg = msg + msg_task
        await message.answer(msg)


async def cmd_add(message: types.Message):
    logger.info(f'Command: <add> - {message.from_user.username}:{message.from_user.id}')
    if debug_mode:
        logger.debug(f'Command: <add> - {message}')
    await message.answer("Enter the task name ✍")
    await TaskManagement.waiting_task_name.set()


async def cmd_close(message: types.Message):
    logger.info(f'Command: <close> - {message.from_user.username}:{message.from_user.id}')
    if debug_mode:
        logger.debug(f'Command: <close> - {message}')
    user_tasks = get_tasks(message.from_user.id)
    msg = "Choose task you want to close (Provide ID) 👇\n\n"
    for task in user_tasks:
        author = ' '.join(filter(None, (task.user.telegram_first_name, task.user.telegram_last_name)))
        msg_task = f"<b>ID:</b> {task.id}\n" \
                   f"<b>Name:</b> {task.name}\n" \
                   f"<b>Description:</b> {task.description}\n" \
                   f"<b>Author:</b> {author}\n\n"
        msg = msg + msg_task
    await message.answer(msg)
    await TaskManagement.waiting_task_close.set()


def register_bot_commands(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"], state='*', is_user=True)
    dp.register_message_handler(cmd_version, commands=["version"], state='*', is_user=True)
    dp.register_message_handler(cmd_id, commands=["id"], state='*', is_user=True)
    dp.register_message_handler(cmd_user, commands=["user"], state='*', is_user=True)
    dp.register_message_handler(cmd_task, commands=["task"], state='*', chat_type='private', is_user=True)
    dp.register_message_handler(cmd_task_all, commands=["task"], state='*', chat_type=['supergroup', 'group'], is_user=True)
    dp.register_message_handler(cmd_add, commands=["add"], state='*', is_user=True)
    dp.register_message_handler(cmd_close, commands=["close"], state='*', is_user=True)
