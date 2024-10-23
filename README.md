# Telegram Ollama Bot

A simple Telegram bot that uses Ollama technology to respond to user messages.

## Description

The bot uses the Telegram API to receive and send messages. When a user sends a message to the bot, it uses Ollama technology to generate a response. The bot supports `/start` and `/help` commands, as well as text messages.

## Installation

1. Clone the repository: `git clone https://github.com/your-username/telegram_ollama_bot.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `bot_info.json` file with your bot token: `{"TOKEN": "your-token-here"}`
4. Run the bot: `python telegram_ollama_bot.py`

## Commands

* `/start` - start a conversation with the bot
* `/help` - get help with bot commands

## Technologies

* Python 3.x
* Telegram API
* Ollama API

## Authors

* Arseny802

## License

* Apache License 2.0

## Links

* [Telegram API](https://core.telegram.org/api)
* [Ollama API](https://ollama.ai/api)

## Notes

* This project is an example of using Ollama technology to create a simple Telegram bot.
* A token is required to run the bot, which can be obtained from the Telegram API.
* The bot only supports text messages and `/start` and `/help` commands.
