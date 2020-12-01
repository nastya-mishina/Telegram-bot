import os
import time

import logging

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def parse_homework_status(homework):
    homework_name = homework.get("homework_name")
    if homework_name is not None:
        if homework.get("status") is not None and homework.get("status") != "approved":
            verdict = "К сожалению в работе нашлись ошибки."
        else:
            verdict = "Ревьюеру всё понравилось, можно приступать к следующему уроку."
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    return "Статус домашнего задания неизвестен."


def get_homework_statuses(current_timestamp):
    base_url = "https://praktikum.yandex.ru/api/user_api/{}/"
    method = "homework_statuses"
    url = base_url.format(method)
    headers = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}
    if current_timestamp is None:
        current_timestamp = time.time()
    params = {"from_date": current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=params)
        return homework_statuses.json()
    except requests.RequestException as ex:
        return logging.error("Error at %s", "request on server praktikum", exc_info=ex)


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    # проинициализировать бота здесь
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get("homeworks"):
                last_homework = new_homework.get("homeworks")[0]
                verdict = parse_homework_status(last_homework)
                send_message(verdict, bot)
            current_timestamp = new_homework.get("current_date", current_timestamp)  # обновить timestamp
            time.sleep(1200)  # опрашивать раз в 20 минут

        except Exception as e:
            print(f"Бот столкнулся с ошибкой: {e}")
            time.sleep(20)


if __name__ == "__main__":
    main()
