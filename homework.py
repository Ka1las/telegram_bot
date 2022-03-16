import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s',
)


def send_message(bot, message):
    """Отправляет сообщение."""
    logger.info(f'Отправка сообщения: {message}')
    bot_message = bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    if not bot_message:
        raise telegram.TelegramError(f'Ошибка при отправке: {message}')
    else:
        logger.info(f'Отправка сообщения: {message}')


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    params = {'from_date': current_timestamp}
    try:
        api_answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
        logging.info('Сервер работает')
        if api_answer.status_code != HTTPStatus.OK:
            raise Exception('Ошибка в коде состояния HTTP')
        return api_answer.json()
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        raise error


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not isinstance(response['homeworks'], list):
        logger.error('Не найден ключ homeworks')
        raise AssertionError('Ключи отсутствуют')
    elif 'current_date' not in response:
        logger.error('Не найден ключ current_date')
        raise AssertionError('Ключи отсутствуют')
    else:
        logger.info('Проверка корректности API пройдена')
    return response.get('homeworks')


def parse_status(homework):
    """Извлекает информацию о статусе работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES.keys():
        logger.error('Такого статуса нет')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Возвращает переменные окружения если они доступны."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствуют переменные окружения!')
        raise SystemExit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if isinstance(homework, list) and homework:
                send_message(bot, parse_status(homework[0]))
            else:
                logger.debug('Статус задания не обновлён')
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        logger.error(f'Непредвиденная ошибка: {error}')
