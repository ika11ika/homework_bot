import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

import exceptions

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

logging.basicConfig(
    filename='main.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)


def send_message(bot, message):
    """Отправка сообщения в Telegram."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
    except telegram.error.TelegramError:
        logging.error('Сообщение не отправлено')
    else:
        logging.info('Сообщение отправлено')


def get_api_answer(current_timestamp):
    """Запрос ответа от API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if homework_statuses.status_code != 200:
        assert False
        logging.error(f'Ошибка при запросе {homework_statuses.status_code}')
    return homework_statuses.json()


def check_response(response):
    """Проверка ответа API на корректность."""
    try:
        homeworks = response['homeworks']
    except KeyError:
        logging.error('В словаре нет ключа homeworks')
    if not homeworks:
        logging.error('В ответе API нет списка работ')
        raise exceptions.APIResponseException()
    if homeworks == []:
        logging.error('Работ не найдено')
        raise exceptions.APIResponseException()
    if type(homeworks) != list:
        logging.error('В ответе API работы представлены не списком')
        raise exceptions.APIResponseException()
    return homeworks


def parse_status(homework):
    """Обработка статуса полученной домашки."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка, что токены найдены."""
    if None in (PRACTICUM_TOKEN, TELEGRAM_TOKEN):
        logging.critical('Отсутствие обязательных переменных окружения')
        return False
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        return
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    response = get_api_answer(current_timestamp)
    homeworks = check_response(response)
    status = parse_status(homeworks[0])
    while True:
        try:
            current_timestamp = int(time.time())
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            message = parse_status(homeworks[0])
            if (message != status):
                send_message(bot, message)
                status = message
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            print(message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
