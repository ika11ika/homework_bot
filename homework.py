import logging
import os
import sys
import time
from http import HTTPStatus

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


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения в Telegram."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
    except telegram.error.TelegramError as error:
        logging.error(TELEGRAM_TOKEN)
        raise exceptions.BotSendMessageException(error)
    else:
        logging.info('Сообщение отправлено')


def get_api_answer(current_timestamp):
    """Запрос ответа от API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': 0}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
        error = f'Ошибка ответа API {homework_statuses.status_code}'
        if homework_statuses.status_code != HTTPStatus.OK:
            raise exceptions.GetAPIAnswerException(error)
    except requests.ConnectionError:
        raise exceptions.GetAPIAnswerException(error)
    return homework_statuses.json()


def check_response(response):
    """Проверка ответа API на корректность."""
    if not response:
        raise exceptions.EmptyResponseExeption('Ответ от API - пустой словарь')
    if type(response) == list:
        response = response[0]
    if 'homeworks' in response:
        homeworks = response['homeworks']
        if type(homeworks) != list:
            message = 'В ответе API работы представлены не списком'
            raise exceptions.APIFormatResponseException(message)
        if homeworks == []:
            raise exceptions.APIFormatResponseException('Работ не найдено')
        return homeworks
    else:
        message = "В ответе запроса API нет ключа 'homeworks'"
        raise exceptions.APIFormatResponseException(message)


def parse_status(homework):
    """Обработка статуса полученной домашки."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status in HOMEWORK_VERDICTS:
        verdict = HOMEWORK_VERDICTS[homework_status]
    else:
        message = 'Нет вердикста для полученного статуса'
        raise exceptions.NoVerdictForStatusException(message)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка, что токены найдены."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        sys.exit("Не удалось загрузить данные токенов.")
    try:
        logging.info(TELEGRAM_TOKEN)
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        current_timestamp = int(time.time())
        response = get_api_answer(current_timestamp)
        homeworks = check_response(response)
        status = parse_status(homeworks[0])
        logging.info("Первая итерация")
        while True:
            current_timestamp = int(time.time())
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            message = parse_status(homeworks[0])
            #if (message != status):
            send_message(bot, message)
            status = message
            logging.info("Очередная итерация цикла")
            time.sleep(RETRY_TIME)
    except Exception as error:
        logging.error(error)
        time.sleep(RETRY_TIME)


if __name__ == '__main__':

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    main()
