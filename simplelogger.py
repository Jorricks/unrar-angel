import logging
import sys


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ActualLogger(object):

    def __init__(self, level='', file='', file2=''):
        if level == '' and file == '':
            self.py_logger.critical('Logger', 'Tried to create new instance of logger')
            text_file = open("/tmp/angel-logger-critical-error", "w")
            text_file.write("%(asctime)s - Logger destination not defined")
            text_file.close()
            sys.exit(2)

        self.level = level
        self.file = file
        self.file2 = file2

        # create logger
        self.py_logger = logging.getLogger('angel-logger')
        self.py_new_file_logger = logging.getLogger('angel-file-logger')
        # update logger
        self.update_logger()
        self.py_logger.info('%-8s' % 'Logger' + ' - ' + 'Started logger')

    def update_logger(self):
        self.py_logger.handlers = []
        self.py_new_file_logger.handlers = []

        self.py_new_file_logger.setLevel(logging.DEBUG)

        # create file handler, set level to debug and add new handler
        fh = logging.FileHandler(self.file, 'a')
        if self.level == "CRITICAL":
            self.py_logger.setLevel(logging.CRITICAL)
            fh.setLevel(logging.CRITICAL)
        elif self.level == "ERROR":
            self.py_logger.setLevel(logging.ERROR)
            fh.setLevel(logging.ERROR)
        elif self.level == "WARNING":
            self.py_logger.setLevel(logging.WARNING)
            fh.setLevel(logging.WARNING)
        elif self.level == "INFO":
            self.py_logger.setLevel(logging.INFO)
            fh.setLevel(logging.INFO)
        else:
            self.py_logger.setLevel(logging.DEBUG)
            fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
        fh.setFormatter(formatter)
        self.py_logger.addHandler(fh)

        fhnf = logging.FileHandler(self.file2, 'a')
        fhnf.setLevel(logging.DEBUG)
        formatter2 = logging.Formatter('%(asctime)s - %(message)s')
        fhnf.setFormatter(formatter2)
        self.py_new_file_logger.addHandler(fhnf)

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

    def new_file(self, config_name, filename, destination_path):
        self.py_new_file_logger.debug(config_name + ' - ' + filename + ' - ' + destination_path)


class SimpleLogger(ActualLogger, metaclass=Singleton):
    pass
