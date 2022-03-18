import logging
import sys
import time
from http import HTTPStatus

import requests
import telegram

from constants import (
    ENDPOINT, HEADERS, PRACTICUM_TOKEN, RETRY_TIME, TELEGRAM_CHAT_ID,
    TELEGRAM_TOKEN
)

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
# убираю на 140стр,тесты падают - NameError: name 'logger' is not defined


class NoKeyError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'NoKeyError, {0} '.format(self.message)
        else:
            return 'NoKeyError, ключ не найден'


class NoConnectionError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'NoConnection {0} '.format(self.message)
        else:
            return 'NoConnection, не упешный запрос ресурса'


def send_message(bot, message):
    """Отправляет сообщение."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Отправка сообщения: {message}')
    except telegram.TelegramError as error:
        message = (f'Ошибка при отправке сообщения: {error}')
        raise telegram.TelegramError(message)


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    params = {'from_date': current_timestamp}
    try:
        api_answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
        logging.info('Сервер работает')
        if api_answer.status_code != HTTPStatus.OK:
            raise NoConnectionError
        return api_answer.json()
    except NoConnectionError:
        logging.error('Ошибка при запросе к основному API')
        raise NoConnectionError


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not isinstance(response['homeworks'], list):
        logger.error('API возвращает не список')
        raise TypeError('Объект несоответствующего типа')
    elif type(response['homeworks']) == dict:
        logger.info('API возвращает словарь')
        raise TypeError('Объект несоответствующего типа')
    elif 'homeworks' not in response:
        logger.error('Не найден ключ homeworks')
        raise NoKeyError
    elif 'current_date' not in response:
        logger.error('Не найден ключ current_date')
        raise NoKeyError
    else:
        logger.info('Проверка корректности API пройдена')
    return response.get('homeworks')


def parse_status(homework):
    """Извлекает информацию о статусе работы."""
    homework_name = homework.get('homework_name')
    if homework_name is None:
        raise KeyError('Ключа с таким именем нет')
    homework_status = homework.get('status')
    if homework_status is None:
        raise KeyError('Ключа с таким именем нет')
    elif homework_status not in HOMEWORK_STATUSES:
        logger.error('Такого статуса нет')
        raise KeyError('Проверьте корректность статуса')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Возвращает переменные окружения если они доступны."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствуют переменные окружения!')
        raise SystemError()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if isinstance(homework, list) and homework:
                send_message(bot, parse_status(homework[0]))
                current_timestamp = response.get('current_date')
            else:
                logger.debug('Статус задания не обновлён')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    try:
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.INFO,
            format='%(asctime)s, %(levelname)s, %(message)s',
        )
        main()
    except Exception as error:
        logger.error(f'Непредвиденная ошибка: {error}')
