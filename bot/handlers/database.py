import datetime

from loguru import logger
from peewee import DoesNotExist

from config import debug_mode
from db_init import mysql_db, User, Task


def test_mysql_connect():
    db_conn_error, db_conn_status = None, None
    try:
        db_conn_status = mysql_db.connect()
        logger.info(f'Check connection to Database - Connection success - <{db_conn_status}>')
    except Exception as err:
        db_conn_error = err
        logger.error(f'Check connection to Database - Connection error - <{db_conn_error}>')
    else:
        mysql_db.close()
    return db_conn_status, db_conn_error


def add_user(message):
    # User can be, but with inactive status
    user = get_user_from_telegram_id(message.forward_from.id)
    if user is None:
        status = User.get_or_create(
            telegram_id=message.forward_from.id,
            defaults={'telegram_username': message.forward_from.username,
                      'telegram_first_name': message.forward_from.first_name,
                      'telegram_last_name': message.forward_from.last_name}
        )
        logger.info(f'Database User - User with telegram ID <{message.forward_from.id}> added to DB.')
    else:
        logger.info(f'Database User - User with telegram ID <{message.forward_from.id}> is in DB. Activating..')
        status = activate_user(user), True
    return status


def del_user(telegram_id):
    user_id = get_user_from_telegram_id(telegram_id)
    if user_id is not None:
        user_id.is_active = False
        user_id.save()
        logger.info(f'Database User - User with telegram ID <{telegram_id}> deactivated')
    return user_id


def activate_user(user):
    user.is_active = True
    user.save()
    logger.info(f'Database User - User with DB ID <{user}> activated')
    return user


def get_user_from_telegram_id(telegram_id):
    try:
        user = User.get(User.telegram_id == telegram_id)
        logger.info(f'Database User - User with telegram ID <{telegram_id}> is in DB')
    except DoesNotExist:
        user = None
        logger.info(f'Database User - There is no user with telegram ID <{telegram_id}> in DB')
    return user


def get_user(user_id):
    try:
        user = User.get(User.id == user_id)
        logger.info(f'Database User - User with ID <{user_id}> is in DB')
    except DoesNotExist:
        user = None
        logger.info(f'Database User - There is no user with ID <{user_id}> in DB')
    return user


def get_users():
    """

    Returns: Peewee model

    """
    query = User.select().where(User.is_active == True)
    logger.info('Database User - Getting all active users from DB')
    return query


def get_user_telegram_ids():
    """

    Returns: List of active users telegram id's

    """
    users = get_users()
    telegram_ids_list = []
    for user in users:
        telegram_id = user.telegram_id
        telegram_ids_list.append(telegram_id)
    logger.info(f'Database User - All active users <{telegram_ids_list}>')
    return telegram_ids_list


def add_task(task_data):
    if debug_mode:
        logger.debug(f'Command: <add> - State new task - <{task_data}>')
    author_id = get_user_from_telegram_id(task_data['task_author'])
    status = Task.get_or_create(
        name=task_data['task_name'],
        defaults={'author_id': author_id,
                  'description': task_data['task_desc'],
                  'assigned_to_id': task_data['task_user']}
    )
    if status[1]:
        logger.info(f'Database Task - New task <{status}> added to DB.')
    else:
        logger.info(f'Database Task - New task error <{status}>')
    return status


def get_tasks(telegram_user_id):
    user_id = get_user_from_telegram_id(telegram_user_id)
    query = Task.select(Task, User).join(User, on=(Task.author_id == User.id), attr='user')\
                .where(Task.assigned_to_id == user_id,
                       Task.is_active == True)
    logger.info('Database Task - Getting all active tasks from DB')
    return query


def get_task(task_id):
    task = Task.get(Task.id == task_id)
    logger.info(f'Database User - Get task with ID <{task_id}> from DB')
    return task


def close_task(task_id):
    try:
        task = get_task(task_id)
        logger.info(f'Database Task - Task with ID <{task_id}> is in DB')
    except DoesNotExist:
        task = False
        logger.info(f'Database Task - There is no task with ID <{task_id}> in DB')
    else:
        task.is_active = False
        task.closed_at = datetime.datetime.now()
        task.save()
        logger.info(f'Database Task - Task <{task}> closed.')
    return task
