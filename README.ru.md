# Telegram Ollama Bot

Это простой бот для Telegram, который использует технологию Ollama для ответа на сообщения пользователей.

## Описание

Бот использует API Telegram для получения и отправки сообщений. Когда пользователь отправляет сообщение боту, он использует технологию Ollama для генерации ответа. Бот поддерживает команды `/start` и `/help`, а также может отвечать на текстовые сообщения.

## Установка

1. Клонируйте репозиторий: `git clone https://github.com/Arseny802/telegram_ollama_bot.git`
2. Установите зависимости: `pip install -r requirements.txt`
3. Создайте файл `config.py` с токеном бота: `TOKEN = 'your-token-here'`
4. Запустите бота: `python telegram_ollama_bot.py`

## Команды

* `/start` - начать диалог с ботом
* `/help` - получить справку по командам бота

## Технологии

* Python 3.x
* Telegram API
* Ollama API

## Авторы

* Arseny802

## Лицензия

* Apache License 2.0

## Ссылки

* [Telegram API](https://core.telegram.org/api)
* [Ollama API](https://ollama.ai/api)

## Примечания

* Этот проект является примером использования технологии Ollama для создания простого бота для Telegram.
* Для работы бота требуется токен, который можно получить в Telegram API.
* Бот поддерживает только текстовые сообщения и команды `/start` и `/help`.
* 