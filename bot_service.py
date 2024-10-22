#!/usr/bin/env python

import sys
from ollama_bot import telegram_ollama_bot

if 'linux' in sys.platform:
    import lin.bot_service_lin as bot_service
elif 'windows' in sys.platform:
    import win.bot_service_win as bot_service
else:
    raise RuntimeError("Unsupported operating system: {}".format(sys.platform))


if __name__ == '__main__':
    bot_service.run_service_command()
    print('Done')
