from loguru import logger
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.database import add_task, get_users, get_user, close_task
from config import debug_mode


class TaskManagement(StatesGroup):
    waiting_task_name = State()
    waiting_task_desc = State()
    waiting_task_worker = State()
    waiting_task_close = State()


async def message_add_task_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['task_name'] = message.text
        data['task_author'] = message.from_user.id
    logger.info(f'Command: <add> - New task name - <{message.from_user.username}:{message.from_user.id}>'
                f' - <{message.text}>')
    if debug_mode:
        logger.debug(f'Command: <add> - New task name - <{message}>')
        logger.debug(f'Saved state data - <{data}>')
    await message.answer("Enter the task description ✍️")
    await TaskManagement.waiting_task_desc.set()


async def message_add_task_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['task_desc'] = message.text
    logger.info(f'Command: <add> - New task description - <{message.from_user.username}:{message.from_user.id}>'
                f' - <{message.text}>')
    if debug_mode:
        logger.debug(f'Command: <add> - New task description - <{message}>')
        logger.debug(f'Saved state data - <{data}>')
    users = get_users()
    inline_kb_users_list = InlineKeyboardMarkup(row_width=2)
    for user in users:
        user_line = ' '.join(filter(None, (user.telegram_first_name, user.telegram_last_name)))
        inline_kb_users_list.add(InlineKeyboardButton(user_line, callback_data=f'{str(user.id)}'))
    await message.answer("Assign to 👷‍♂️", reply_markup=inline_kb_users_list)
    await TaskManagement.waiting_task_worker.set()


async def callback_add_task_user(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['task_user'] = callback_query.data
    logger.info(f'Command: <add> - Callback Query - <{callback_query.from_user.username}:{callback_query.from_user.id}>'
                f' - <{callback_query.data}>')
    if debug_mode:
        logger.debug(f'Command: <add> - Callback Query - <{callback_query}>')
        logger.debug(f'Saved state data - <{data}>')
    await state.finish()
    adding_status = add_task(data)
    if adding_status[1]:
        await callback_query.message.edit_text(text='Task added 💪')
        user = get_user(data['task_user'])
        task = adding_status[0]
        author = ' '.join(filter(None, (callback_query.from_user.first_name, callback_query.from_user.last_name)))
        await callback_query.bot.send_message(user.telegram_id,
                                              "You have new task! 🤘\n"
                                              f"<b>Name:</b> {task.name}\n"
                                              f"<b>Description:</b> {task.description}\n"
                                              f"<b>Author:</b> {author}\n\n")
        logger.info(f'Message send - New task {task.name} sent to <{author}>')
    else:
        await callback_query.message.edit_text(text='Something goes wrong, contact the administrator 👻')


async def message_close_task(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['close_task_id'] = message.text
    logger.info(f'Command: <close> - Task ID - <{message.from_user.username}:{message.from_user.id}>'
                f' - <{message.text}>')
    if debug_mode:
        logger.debug(f'Command: <close> - Task ID - <{message}>')
        logger.debug(f'Saved state data - <{data}>')
    task = close_task(data['close_task_id'])
    if task:
        await message.answer("Task closed! Great job! 🍻️")
        author = get_user(task.author_id)
        user = get_user(task.assigned_to_id)
        user_fullname = ' '.join(filter(None, (user.telegram_first_name, user.telegram_last_name)))
        await message.bot.send_message(author.telegram_id,
                                 f'{user_fullname} closed the task "{task.name}" 🥳')
    else:
        await message.answer("There is no such task ID. 🤷‍♂️")
    await state.finish()


def register_tasks(dp: Dispatcher):
    dp.register_message_handler(message_add_task_name, state=TaskManagement.waiting_task_name, is_user=True)
    dp.register_message_handler(message_add_task_desc, state=TaskManagement.waiting_task_desc, is_user=True)
    dp.register_callback_query_handler(callback_add_task_user, lambda c: c.data,
                                       state=TaskManagement.waiting_task_worker, is_user=True)
    dp.register_message_handler(message_close_task, state=TaskManagement.waiting_task_close, is_user=True)
