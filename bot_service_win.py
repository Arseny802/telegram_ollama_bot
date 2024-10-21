#!/usr/bin/env python

import sys
if 'linux' in sys.platform:
    import os
elif 'windows' in sys.platform:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
else:
    raise RuntimeError("Unsupported operating system: {}".format(sys.platform))

import socket
import asyncio
from ollama_bot import arseny802_ollama_bot


class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "telegram_ollama_bot"
    _bot = arseny802_ollama_bot()

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        try:
            self._bot.main()
        except Exception as e:
            servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE,
                                  servicemanager.PYS_SERVICE_STOPPED,
                                  (self._svc_name_,str(e)))
            print(e)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)


def create_linux_daemon():
    pass


if __name__ == '__main__':
    if 'linux' in sys.platform:
        create_linux_daemon()
    elif 'windows' in sys.platform:
        win32serviceutil.HandleCommandLine(AppServerSvc)
    else:
        raise RuntimeError("Unsupported operating system: {}".format(sys.platform))
    
    print('Done')
