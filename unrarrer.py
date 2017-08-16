import os
from simplelogger import SimpleLogger
from configer import Config
from unrar import rarfile
from unrar import unrarlib


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ActualUnRAR:
    def __init__(self):
        self.logger = SimpleLogger()
        self.logger.info('UnRAR', 'Initiating UnRAR class')
        self.config = Config()
        self.files = []
        self.watcher_config = []
        self.last_size = []
        self.error_count = []

    def add_new_file_to_unrar(self, file, config):
        self.files.append(file)
        self.watcher_config.append(config)
        self.error_count.append(0)
        try:
            file_info = os.stat(file)
            self.last_size.append(file_info.st_size)
            self.logger.info('UnRAR', 'Added {}'.format(file))
        except OSError as e:
            del self.files[len(self.files) - 1]
            del self.watcher_config[len(self.watcher_config) - 1]
            del self.error_count[len(self.error_count) - 1]
            self.logger.error('UnRAR', 'Could not find {}, {}'.format(e.filename, e.strerror))

    def check_if_unrar_possible(self):
        i = 0
        if len(self.files) > 0:
            self.logger.debug('UnRAR', 'Checking if unrar is possible for any of the {} files in queue'
                              .format(len(self.files)))
        while i < len(self.files):
            try:
                file_info = os.stat(self.files[i])
                if file_info.st_size >= 0:
                    if file_info.st_size == self.last_size[i]:
                        if self.unrar_file(i, self.error_count[i]):
                            del self.files[i]
                            del self.watcher_config[i]
                            del self.last_size[i]
                            i -= 1  # after deletion the next item is at row i, so (-1+1=0) gives the next element
                        else:
                            self.error_count[i] += 1
                            self.logger.info('UnRAR',
                                             'Encountered an error. Will keep trying for file {}'
                                             .format(e.filename, e.strerror))
                    else:  # This is to prevent unnecessary unrar attempts.
                        self.last_size[i] = file_info.st_size
                i += 1
            except OSError as e:  # Error if file does not exist.
                del self.files[i]
                del self.watcher_config[i]
                del self.last_size[i]
                del self.error_count[i]
                self.logger.error('UnRAR', 'Could not find {}, {}'.format(e.filename, e.strerror))

    def unrar_file(self, i, error_count):
        try:
            if not rarfile.is_rarfile(self.files[i]):
                if error_count == 0:
                    self.logger.error('UnRAR', 'The following file is not a rarfile (yet): {}'.format(self.files[i]))
            else:
                rar = rarfile.RarFile(self.files[i])
                if rar.testrar() is not None:
                    if error_count == 0:
                        self.logger.error('UnRAR', 'Inside the rarfile there is a bad file named : {}'
                                          .format(rar.testrar()))
                else:
                    # Option to only extract certain files.. Future work.
                    if error_count > 0:
                        self.logger.info('UnRAR', 'The following rarfile became complete : {}'
                                         .format(self.files[i]))
                    self.logger.info('UnRAR', 'Started unrarring : {}'.format(self.files[i]))

                    unrar_path = self.config.get_config_watcher(
                        self.watcher_config[i],
                        'destination_path')
                    self.logger.debug('UnRAR', 'Destination path : {}'.format(unrar_path))

                    try:
                        rar.extractall(path=unrar_path)
                    except Exception as e:
                        print('Errors encountered during unrar: {}'.format(e))

                    self.logger.info('UnRAR', 'Finished unrarring : {}'.format(self.files[i]))
                    return True

        except (rarfile.BadRarFile, unrarlib.UnrarException) as e:
            print('Errors encountered during unrar: {}'.format(e))
        return False


class UnRAR(ActualUnRAR, metaclass=Singleton):
    pass
