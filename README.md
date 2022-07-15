# telegram_bot
## Описание проекта
Написан Telegram-бот, который будет обращаться к API сервиса Практикум.Домашка и узнавать статус вашей домашней работы: взята ли ваша домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.


## Используемые технологии
- flake8==3.9.2
- flake8-docstrings==1.6.0
- pytest==6.2.5
- python-dotenv==0.19.0
- python-telegram-bot==13.7
- requests==2.26.0

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Ka1las/telegram_bot.git
```

```
cd telegram_bot
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
