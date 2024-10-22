#~/python-venvs/ollama/bin/ python

import os
import grp
import lockfile
import daemon
import signal
from ollama_bot import telegram_ollama_bot



def create_linux_daemon():
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    context = daemon.DaemonContext(
        working_directory=current_dir_path,
        umask=0o002,
        pidfile=lockfile.FileLock('/var/run/telegram_ollama_bot.pid'),
        )
    
    bot = telegram_ollama_bot()
    context.signal_map = {
        signal.SIGTERM: bot.cleanup,
        signal.SIGHUP: 'terminate',
        signal.SIGUSR1: bot.reload,
        }
    
    mail_gid = grp.getgrnam('mail').gr_gid
    context.gid = mail_gid
    
    important_file = open('../bot_info.json', 'wb+')
    interesting_file = open('logs/telegram_ollama_bot.log', 'w')
    context.files_preserve = [important_file, interesting_file]
    
    with context:
        bot.main()


def run_service_command():
    create_linux_daemon()

if __name__ == '__main__':
    run_service_command()
    print('Done')
