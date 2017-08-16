import os
from simplelogger import SimpleLogger
from config import Config


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ActualUnRAR:
    def __init__(self):
        self.logger = SimpleLogger()
        self.config = Config()
        self.files = []
        self.watcher_config = []
        self.lastSize = []

    def add_new_file_to_unrar(self, file, config):
        self.files.append(file)
        self.watcher_config.append(config)
        try:
            file_info = os.stat(file)
            self.lastSize.append(file_info.st_size)
        except OSError as e:
            self.lastSize.append(-5-1)  # 5 seconds -1 for extra
            self.logger.error('UnRAR', 'Could not find {}, {}'.format(e.filename, e.strerror))
        self.logger.info('UnRAR', 'Added {}'.format(file))

    def check_if_unrar_possible(self):
        i = 0
        while i < len(self.files):
            try:
                file_info = os.stat(self.files[i])
                if file_info.st_size >= 0:
                    if file_info.st_size == self.lastSize[i]:
                        if self.unrar_file(i):
                            del self.files[i]
                            del self.watcher_config[i]
                            del self.lastSize[i]
                    else:
                        self.lastSize[i] = file_info.st_size
                else:
                    if self.lastSize[i] == -1:
                        del self.files[i]
                        del self.watcher_config[i]
                        del self.lastSize[i]
                    self.lastSize[i] = self.lastSize[i] + 1
            except OSError as e:
                self.logger.error('UnRAR', 'Could not find {}, {}'.format(e.filename, e.strerror))

    def unrar_file(self, i):
        self.logger.info('UnRAR', 'Fake unrar')
        return True


class UnRAR(ActualUnRAR, metaclass=Singleton):
    pass
