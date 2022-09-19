import datetime
import pymysql

from peewee import *

from config import database, username, password, host, port


mysql_db = MySQLDatabase(database,
                         user=username, password=password,
                         host=host, port=int(port))


class BaseModel(Model):
    class Meta:
        database = mysql_db


class User(BaseModel):
    telegram_id = BigIntegerField(null=False, unique=True)
    telegram_username = CharField(null=True)
    telegram_first_name = CharField(null=True)
    telegram_last_name = CharField(null=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'Users'


class Task(BaseModel):
    author_id = ForeignKeyField(User)
    assigned_to_id = ForeignKeyField(User)
    name = CharField(null=False, unique=True)
    description = TextField(null=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.now())
    closed_at = DateTimeField(default=None)

    class Meta:
        db_table = 'Tasks'


if __name__ == "__main__":
    try:
        mysql_db.create_tables([User, Task])
        print("Tables created successfully")
    except Exception as error:
        print("Error:", error)
