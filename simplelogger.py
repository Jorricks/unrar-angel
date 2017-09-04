import logging
import sys


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ActualLogger(object):

    def __init__(self, level='', file=''):
        if level=='' and file=='':
            self.py_logger.critical('Logger', 'Tried to create new instance of logger')
            text_file = open("/tmp/angel-logger-critical-error", "w")
            text_file.write("%(asctime)s - Logger destination not defined")
            text_file.close()
            sys.exit(2)

        self.level = level
        self.file = file

        # create logger
        self.py_logger = logging.getLogger('angel-logger')
        # update logger
        self.update_logger()
        self.py_logger.info('%-8s' % 'Logger' + ' - ' + 'Started logger')

    def update_logger(self):
        self.py_logger.setLevel(self.level)
        self.py_logger.handlers = []

        # create file handler, set level to debug and add new handler
        fh = logging.FileHandler(self.file, 'a')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
        fh.setFormatter(formatter)
        self.py_logger.addHandler(fh)

    def debug(self, system, message):
        self.py_logger.debug('%-8s' % system.upper() + ' - ' + message)

    def info(self, system, message):
        self.py_logger.info('%-8s' % system.upper() + ' - ' + message)

    def warning(self, system, message):
        self.py_logger.warning('%-8s' % system.upper() + ' - ' + message)

    def error(self, system, message):
        self.py_logger.error('%-8s' % system.upper() + ' - ' + message)

    def critical(self, system, message):
        self.py_logger.critical('%-8s' % system.upper() + ' - ' + message)


class SimpleLogger(ActualLogger, metaclass=Singleton):
    pass
