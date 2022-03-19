import logging
import sys
import time
from http import HTTPStatus

import requests
import telegram

from constants import (
    ENDPOINT, HEADERS, PRACTICUM_TOKEN, RETRY_TIME, TELEGRAM_CHAT_ID,
    TELEGRAM_TOKEN, HOMEWORK_STATUSES
)
from exceptions import NoConnectionError, NoKeyError, No200Error


def send_message(bot, message):
    """Отправляет сообщение."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f'Отправка сообщения: {message}')
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
            raise No200Error
        return api_answer.json()
    except NoConnectionError:
        logging.error('Ошибка при запросе к основному API')
        raise NoConnectionError


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not isinstance(response['homeworks'], list):
        logging.error('API возвращает не список')
        raise TypeError('Объект несоответствующего типа')
    elif isinstance(response['homeworks'], dict):
        logging.info('API возвращает словарь')
        raise TypeError('Объект несоответствующего типа')
    elif 'homeworks' not in response:
        logging.error('Не найден ключ homeworks')
        raise NoKeyError
    elif 'current_date' not in response:
        logging.error('Не найден ключ current_date')
        raise NoKeyError
    logging.info('Проверка корректности API пройдена')
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
        logging.error('Такого статуса нет')
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
        logger = logging.getLogger(__name__)
        main()
    except Exception as error:
        logging.error(f'Непредвиденная ошибка: {error}')
