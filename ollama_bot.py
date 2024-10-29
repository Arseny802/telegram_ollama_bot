#~/python-venvs/ollama/bin/ python
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

import os
import sys
import time
import json
import pathlib
import signal
import logging
import logging.handlers

import ollama

from telegram import ForceReply, Update, Message
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext


INTERRUPT_SIGNAL_OCCURED = False

def get_project_directory():      
    """
    Returns the absolute path to the directory containing the current file.

    This function resolves the parent directory of the current file (__file__)
    and returns it as an absolute path using pathlib.
    """
    return pathlib.Path(__file__).parent.resolve()


def create_log_formatter() -> logging.Formatter:
    format = "[%(asctime)s] [%(name)s] [%(levelname)s] [%(funcName)s(%(lineno)d)]: %(message)s"
    format_date = "%d-%m-%YT%H:%M:%S"
    return logging.Formatter(format, format_date)


class telegram_ollama_bot:
    BOT_INFO_FILE = "bot_info.json"
    _logger: logging.Logger
    token: str

    def __init__(self, log_dir_path = None):
        """
        Initializes the bot.

        This method enables logging, loads the bot information from a file,
        initializes the bot handlers, and creates an instance of the OLLAMA API client.

        :param log_dir_path: The directory path to save the logs in. If not provided,
            the logs will be saved in the "logs" directory in the current working
            directory.
        """
        self._enable_logging(log_dir_path)
        self._load_bot_info()
        self._init_bot_handlers()
        self.client = ollama.Client()


    def _enable_logging(self, dir_path: os.PathLike = None):
        """
        Enables logging for the bot.

        This method sets up the logging system for the bot. If `dir_path` is
        not specified, the logs will be saved in the `logs` directory in the
        same directory as the current file.

        If the `dir_path` directory does not exist, it will be created.

        The logs will be saved in a file named `telegram_ollama_bot.log` in
        the specified directory.

        The logging level is set to `INFO` by default, but you can change it
        by modifying the `logging.basicConfig` call.

        Note that the logging level for the `httpx` library is set to `WARNING`
        to avoid logging all GET and POST requests.
        """
        if not dir_path:
            dir_path = get_project_directory() / "logs"

        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        logs_path = os.path.join(dir_path, "telegram_ollama_bot.log")
        print(f"Logs will be saved in {logs_path}")


        max_size = 100 * 1024 * 1024 # 100 MB
        file_handler = logging.handlers.RotatingFileHandler(
            logs_path, mode='a', maxBytes=max_size, backupCount=10, encoding="UTF-8", delay=0)
        file_handler.setFormatter(create_log_formatter())
        file_handler.setLevel(logging.INFO)

        root_log = logging.getLogger('telegram_ollama_bot')
        root_log.setLevel(logging.INFO)
        root_log.addHandler(file_handler)
        root_log.removeHandler(sys.stdout)
        root_log.removeHandler(sys.stderr)
        
        # set higher logging level for httpx to avoid all GET and POST requests being logged
        log_httpx = logging.getLogger("httpx")
        log_httpx.setLevel(logging.WARNING)
        log_httpx.addHandler(file_handler)
        log_httpx.removeHandler(sys.stdout)
        log_httpx.removeHandler(sys.stderr)

        self._logger = root_log

    def _load_bot_info(self):
        """
        Loads bot info from a JSON file.

        Loads bot info from a file at the path specified by `BOT_INFO_FILE`. The
        file should contain a JSON object with a single key, "token", which is the
        bot token.

        If the file does not exist, or if the file does not contain the bot token,
        a warning will be logged and the bot will not start.

        :return: None
        """
        filepath = str(get_project_directory() / self.BOT_INFO_FILE)
        if not os.path.exists(filepath):
            self._logger.warning(f"Error! No bot info file found at {filepath}")
            return
        
        with open(filepath, 'r', encoding='utf-8') as reader:
            self._bot_info = json.load(reader)
        
        if self._bot_info is None or self._bot_info.get("token") is None:
            self._logger.warning(f"Error! No bot token provided.")
            return
        
        self.token = self._bot_info["token"]
        self._logger.info(f"Bot token: {self.token}")

    def _init_bot_handlers(self):
        """
        Initialize the Telegram bot application and its handlers.

        This method creates a Telegram bot application and sets up its handlers. The
        handlers are responsible for responding to user commands and messages.

        The following handlers are set up:
        * CommandHandler for the /start command
        * CommandHandler for the /help command
        * MessageHandler for any non-command messages

        The handlers are passed the `start` and `help_command` methods of this class
        as their callback functions. The `pass_to_ollama` method is used as the callback
        function for the MessageHandler.

        :return: None
        """
        # Create the Application and pass it your bot's token.
        self.application = Application.builder().token(self.token).build()

        # on different commands - answer in Telegram
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))

        # on non command i.e message - echo the message on Telegram
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.pass_to_ollama))


    # Define a few command handlers. These usually take the two arguments update and
    # context.
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        self._logger.info("User %s started the bot", str(update.effective_chat))
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.mention_html()}!",
            reply_markup=ForceReply(selective=True),
        )
        context.bot.set_chat_photo(update.effective_user.id,
                                   photo=str(get_project_directory() / "res" / "icon.jpeg"))


    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        self._logger.info("User %s asked for help", str(update.effective_chat))
        await update.message.reply_text("Help!")


    async def pass_to_ollama(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Echo the user message."""
        self._logger.info("User %s echoed", str(update.effective_chat))
        message: str = update.message.text

        prepare_message = "Готовлю ответ, подождите..."
        self._logger.info("User asked: %s", message)
        try:
            response_mesasge = await update.message.reply_markdown(
                prepare_message, reply_to_message_id=update.message.message_id)
            response = self.client.generate(
                model='gemma2:27b',
                prompt=message,
                stream=True,
                #messages=[
                #    {
                #        'role': 'user',
                #        'content': message,
                #        'temperature': 0.75,
                #        'logit': 0.75,
                #    }],
                keep_alive="1h"
            )
            
            full_answer_text = ""
            appended_text = ""
            counter = 0
            last_wrote = 0
            counter_max = 10
            elapsed_time_max = 2
            for answer in response:
                self._logger.info("Ollama answered: %s", answer)
                answer_text = answer["response"]
                counter += 1

                appended_text += answer_text
                if not appended_text or not appended_text.strip() or not appended_text.rstrip():
                    continue

                if counter <= counter_max or time.time() - last_wrote < elapsed_time_max:
                    continue

                full_answer_text += appended_text
                await response_mesasge.edit_text(full_answer_text)

                appended_text = ""
                counter = 0
                last_wrote = time.time()
                
            full_answer_text += appended_text
            try:
                await update.message.reply_markdown(full_answer_text, reply_to_message_id=update.message.message_id)
                await response_mesasge.delete()
            except Exception as ex:
                self._logger.error(ex)
                if appended_text.strip() and appended_text.rstrip():
                    await response_mesasge.edit_text(full_answer_text)
                    self._logger.info("Edited previous message")
            finally:
                self._logger.info("Full answer: %s", full_answer_text)
        except Exception as e:
            self._logger.error(e)
            await update.message.reply_markdown("Sorry, I can't answer that :(")


    def main(self) -> None:
        """Start the bot."""
        self._logger.info("Starting the bot...")
        self.application.run_polling(
            timeout=60, 
            allowed_updates=Update.ALL_TYPES, 
            stop_signals=[signal.SIGINT, signal.SIGTERM, signal.SIGABRT])
        self._logger.info("Shutting down...")
        self.application.stop_running()

    def cleanup(self):
        """
        Clean up resources allocated by the bot.

        This method closes the connection to the OLLAMA API and other resources
        allocated by the bot. It is called when the bot is shut down.
        """
        self.client.close()

    def reload(self):
        """
        Reload bot configuration from file.

        This method reloads the bot configuration from the file specified
        in `BOT_INFO_FILE`. It is used to reload the configuration when the
        file changes without restarting the bot.

        This method is a coroutine.
        """
        self._load_bot_info()
        self._init_bot_handlers()

def interrupt_handler(signum, frame):
    logging.getLogger("main").info(f'Handling signal {signum} ({signal.Signals(signum).name}).')
    INTERRUPT_SIGNAL_OCCURED = True
    # do whatever...
    time.sleep(1)

def set_signal_handlers():
    signal.signal(signal.SIGINT, interrupt_handler)
    signal.signal(signal.SIGTERM, interrupt_handler)
    signal.signal(signal.SIGABRT, interrupt_handler)

if __name__ == "__main__":
    print("Run main with arguments: ", sys.argv)
    log_path = get_project_directory() / "logs"
    if len(sys.argv) > 1:
        log_path = sys.argv[1]
        
    main_log = logging.getLogger("main")
    main_log.setLevel(logging.INFO)
    [h.setFormatter(create_log_formatter()) for h in main_log.handlers]

    finish_ok = False
    set_signal_handlers()
    while not finish_ok:
        main_log.info("Starting main...")
        bot = telegram_ollama_bot(log_path)
        try:
            # Run the bot until the user presses Ctrl-C or SystemExit
            bot.main()
            finish_ok = True
        except KeyboardInterrupt:
            main_log.info("KeyboardInterrupt occurred. Passing it.")
        except SystemExit as se:
            main_log.warning("SystemExit: %s", se)
            break
        except Exception as e:
            main_log.error(e)
        finally:
            if not INTERRUPT_SIGNAL_OCCURED and not finish_ok:
                main_log.info("Continue bot loop.")
                time.sleep(10)
            else:
                main_log.info("Exit bot loop.")
                break
