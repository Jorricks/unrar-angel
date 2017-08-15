import logging


class SingletonLogger(object):
    class __OnlyOne:
        def __init__(self, level, file):
            self.level = level
            self.file = file

    instance = None

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __init__(self, level, file):
        if not self.instance:
            self.instance = self.__OnlyOne(level, file)
        else:
            self.instance.level = level
            self.instance.file = file

        # create logger
        self.py_logger = logging.getLogger('angel-logger')
        # update logger
        self.update_logger()

    def update_logger(self):
        self.py_logger.setLevel(self.instance.level)
        self.py_logger.handlers = []

        # create file handler, set level to debug and add new handler
        fh = logging.FileHandler(self.instance.file, 'a')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s')
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
