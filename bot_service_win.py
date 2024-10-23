#!/usr/bin/env python

import win32serviceutil
import win32service
import win32event
import servicemanager

import sys
import socket
import asyncio

from ollama_bot import telegram_ollama_bot


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


def run_service_command():
    win32serviceutil.HandleCommandLine(AppServerSvc)


if __name__ == '__main__':
    run_service_command()
    print('Done')
