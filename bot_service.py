#!/usr/bin/env python

import sys
if 'linux' in sys.platform:
    raise RuntimeError("Create service with shell script in 'lin' folder.")
elif 'windows' in sys.platform:
    import bot_service_win as bot_service
else:
    raise RuntimeError("Unsupported operating system: {}".format(sys.platform))


if __name__ == '__main__':
    bot_service.run_service_command()
    print('Done')
