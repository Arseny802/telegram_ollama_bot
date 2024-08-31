#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import json
import os
import logging
import pathlib

import ollama

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


class arseny802_ollama_bot:
    BOT_INFO_FILE = "bot_info.json"
    logger: logging.Logger
    token: str

    def _enable_logging(self, dir_path: str = None):
        if not dir_path:
            dir_path = pathlib.Path(__file__).parent.resolve() / "logs"

        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        logs_path = str(dir_path / "arseny802_ollama_bot.log")
        print(f"Logs will be saved in {logs_path}")

        logging.basicConfig(
            filename = logs_path,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO,
            encoding="utf-8",
            datefmt="%d-%m-%Y %H:%M:%S",
        )
        # set higher logging level for httpx to avoid all GET and POST requests being logged
        logging.getLogger("httpx").setLevel(logging.WARNING)

        self.logger = logging.getLogger(__name__)

    def _load_bot_info(self):
        with open(self.BOT_INFO_FILE, 'r', encoding='utf-8') as reader:
            self._bot_info = json.load(reader)
        self.token = self._bot_info["token"]
        self.logger.info(f"Bot token: {self.token}")


    # Define a few command handlers. These usually take the two arguments update and
    # context.
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        self.logger.info("User %s started the bot", str(update.effective_chat))
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.mention_html()}!",
            reply_markup=ForceReply(selective=True),
        )


    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        self.logger.info("User %s asked for help", str(update.effective_chat))
        await update.message.reply_text("Help!")


    async def pass_to_ollama(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Echo the user message."""
        self.logger.info("User %s echoed", str(update.effective_chat))
        message: str = update.message.text

        self.logger.info("User asked: %s", message)
        response = ollama.chat(model='llama3.1', messages=[
            {
                'role': 'user',
                'content': message,
            },
        ])
        answer = response['message']['content']
        self.logger.info("Ollama answered: %s", answer)

        await update.message.reply_text(answer)


    def main(self) -> None:
        """Start the bot."""
        # Create the Application and pass it your bot's token.

        self._enable_logging()
        self._load_bot_info()

        application = Application.builder().token(self.token).build()

        # on different commands - answer in Telegram
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))

        # on non command i.e message - echo the message on Telegram
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.pass_to_ollama))

        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = arseny802_ollama_bot()
    bot.main()