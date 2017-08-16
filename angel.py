#!/usr/bin/env python

import sys, time
from daemon import Daemon
from simplelogger import SimpleLogger
from configer import Config
from watcher import Watcher


class MyDaemon(Daemon):
    def run(self):
        self.logger.info('Daemon', 'Starting the actual process')

        watcher = Watcher(self.logger, self.config)
        try:
            while True:
                watcher.run()
                self.logger.info('Angel', 'Reloading watchers')
                if self.config.get_amount_of_active_watchers() == 0:
                    self.logger.critical('Angel', 'There are no watchers to be started, quiting')
                    break
        except:
            self.logger.critical('Angel', 'Watcher ended, daemon has been beheaded')


if __name__ == "__main__":
    config = Config()
    logger = SimpleLogger(config.get_config_global('logging_level'),
                          config.get_config_global('logging_path'))
    config.set_logger(logger)

    daemon = MyDaemon(config.get_config_global('angel_pid_path'), logger, config)
    print(config.get_config_global('program_name'), end=' ')

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print('starting\n')
            logger.info('Angel', 'Starting '+config.get_config_global('program_name'))
            daemon.start()

        elif 'stop' == sys.argv[1]:
            print('stopping\n')
            logger.info('Angel', 'Stopping '+config.get_config_global('program_name'))
            daemon.stop()

        elif 'restart' == sys.argv[1]:
            print('restarting\n')
            logger.info('Angel', 'Restarting '+config.get_config_global('program_name'))
            daemon.restart()

        else:
            print("\n\nUnknown command")
            logger.info('Angel', config.get_config_global('program_name') +
                        ' received an unsupported parameter "{}"'.format(sys.argv[1]))
            sys.exit(2)
        sys.exit(0)
    else:
        print("\n\n", "Usage: %s start|stop|restart" % sys.argv[0])
        logger.info('Angel', 'Tried to start UnRAR Angel without parameters, which is unsupported')
        sys.exit(2)
