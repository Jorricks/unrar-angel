#!/usr/bin/env python

import sys, time
from daemon import Daemon
from simplelogger import SimpleLogger
from config import Config
from watcher import Watcher


class MyDaemon(Daemon):
    def run(self):
        self.logger.info('Daemon', 'Starting the actual process 2')

        watcher = Watcher(self.logger, self.config)
        watcher.run()

        self.logger.critical('Angel', 'Watcher ended, daemon has been beheaded')


if __name__ == "__main__":
    config = Config()
    logger = SimpleLogger('DEBUG', '/tmp/angel-logger.log')

    daemon = MyDaemon('/tmp/unrar-angel.pid', logger, config)
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
