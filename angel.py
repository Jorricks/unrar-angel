#!/usr/bin/env python

import sys, time
from daemon import Daemon
from logger import SingletonLogger


class MyDaemon(Daemon):
    def run(self):
        while True:
            with open("/tmp/current_time.txt", "w") as f:
                f.write("The time is now " + time.ctime())
            time.sleep(1)


if __name__ == "__main__":
    logger = SingletonLogger('DEBUG', '/tmp/angel-logger.log')
    daemon = MyDaemon('/tmp/unrar-angel.pid', logger)
    print('UnRAR angel', end=' ')

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print('starting\n')
            logger.info('Angel', 'Starting UnRAR Angel')
            daemon.start()

        elif 'stop' == sys.argv[1]:
            print('stopping\n')
            logger.info('Angel', 'Stopping UnRAR Angel')
            daemon.stop()

        elif 'restart' == sys.argv[1]:
            print('restarting\n')
            logger.info('Angel', 'Restarting UnRAR Angel')
            daemon.restart()

        else:
            print("\n\nUnknown command")
            logger.info('Angel' 'UnRAR Angel received an unsupported parameter "{}"'.format(sys.argv[1]))
            sys.exit(2)
        sys.exit(0)
    else:
        print("\n\nusage: %s start|stop|restart" % sys.argv[0])
        logger.info('Angel' 'Tried to start UnRAR Angel without parameters, which is unsupported'.format(sys.argv[1]))
        sys.exit(2)
