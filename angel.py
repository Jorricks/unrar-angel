#!/usr/bin/env python

import sys
import traceback

from simplelogger import SimpleLogger
from configer import Config
from watcher import Watcher


class MyDaemon:
    def __init__(self, main_logger, main_config):
        self.logger = main_logger
        self.config = main_config

    def run(self):
        self.logger.info('Angel', 'Starting the actual process')

        watcher = Watcher(self.logger, self.config)
        self.config.start_web_server()
        try:
            while True:
                self.logger.info('Angel', 'Loading watchers')
                if self.config.get_amount_of_active_watchers() == 0:
                    self.logger.critical('Angel', 'There are no watchers to be started, quiting')
                    break
                else:
                    watcher.run()
                    self.logger.info('Angel', 'Going to reload the watchers')
        except Exception:
            self.logger.critical('Angel', 'Watcher ended, daemon has been beheaded')
            self.logger.critical('Angel', traceback.format_exc())
            self.logger.critical('Angel', sys.exc_info()[0])



if __name__ == "__main__":
    config = Config()
    logger = SimpleLogger(config.get_config_global('logging_level'),
                          config.get_config_global('logging_path'),
                          config.get_config_global('logging_path_new_files'))
    config.set_logger(logger)

    daemon = MyDaemon(logger, config)
    print(config.get_config_global('program_name'), end=' ')

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print('starting\n')
            logger.info('Angel', 'Starting ' + config.get_config_global('program_name'))
            daemon.run()

        # elif 'stop' == sys.argv[1]:
        #     print('stopping\n')
        #     logger.info('Angel', 'Stopping ' + config.get_config_global('program_name'))
        #     daemon.stop()
        #
        # elif 'restart' == sys.argv[1]:
        #     print('restarting\n')
        #     logger.info('Angel', 'Restarting ' + config.get_config_global('program_name'))
        #     daemon.restart()
        #
        # elif 'status' == sys.argv[1]:
        #     print("status\n")
        #     pid = daemon.get_pid()
        #     logger.info('Angel', 'Requested ' + config.get_config_global('program_name') + ' daemon status')
        #     if pid is None:
        #         logger.info('Angel', config.get_config_global('program_name') + ' daemon not running')
        #         print(config.get_config_global('program_name') + ' daemon not running')
        #     else:
        #         logger.info('Angel', config.get_config_global('program_name') + ' daemon is running wih pid %d' % pid)
        #         print(config.get_config_global('program_name') + ' daemon is running wih pid %d' % pid)

        elif 'verify_program' == sys.argv[1]:
            print('verifying program\n')
            logger.info('Angel', 'Verifying the current state of the program')
            imported = getattr(__import__('verify_ready', fromlist=['VerifyInstallation']), 'VerifyInstallation')
            verifier = imported(config)
            sys.exit(2)

        else:
            print("\n\nUnknown command")
            print("\n\nUsage: %s start|verify_program" % sys.argv[0])
            logger.info('Angel', config.get_config_global('program_name') +
                        ' received an unsupported parameter "{}"'.format(sys.argv[1]))
            sys.exit(2)
        sys.exit(0)
    else:
        print("\n\nUsage: %s start|verify_program" % sys.argv[0])
        logger.info('Angel', 'Tried to start UnRAR Angel without parameters, which is unsupported')
        sys.exit(2)
