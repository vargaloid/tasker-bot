## Telegram tasker bot for small projects

### Requirements
* python 3.7
* * aiogram 2.21
* * loguru 0.6.0
* * peewee 3.15.1
* * PyMySQL 1.0.2
* MySQL/MariaDB

### How to install
1. Clone the repository;
2. Create database and user:
```SQL
CREATE DATABASE db_name;
GRANT ALL PRIVILEGES ON db_name.* TO db_user@localhost IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
```
3. Manually add first telegram user for bot:
```SQL
INSERT INTO db_name.Users(telegram_id,telegram_username,telegram_first_name,telegram_last_name,is_active,created_at)
VALUES (your_telegram_id,'your_username','your_firstname',your_lastname,True,CURRENT_TIMESTAMP);
```
4. Create bot config file and fill it in:
`mv tasker-bot/config.py.example tasker-bot/config.py`
5. Move systemd service unit `systemd/tasker-bot.service` to `/etc/systemd/system/`
5. Fill in the required data in `/etc/systemd/system/tasker-bot.service`
6. Reload systemd `systemctl daemon-reload`
7. Start daemon `systemctl start tasker-bot.service`
