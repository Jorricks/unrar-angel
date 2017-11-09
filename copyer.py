import os
from simplelogger import SimpleLogger
from configer import Config
from notifier import Notifier
from shutil import copyfile
import re


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ActualCopyer:
    def __init__(self):
        self.logger = SimpleLogger()
        self.logger.info('Copyer', 'Initializing Copyer class')
        self.config = Config()
        self.notifier = Notifier(self.logger, self.config)
        self.files = []
        self.watcher_config = []
        self.last_size = []

    def add_new_file(self, file, config):
        if self.config.get_config_watcher(config, 'copy_match_everything') != 1:
            regex = self.config.get_config_watcher(config, 'copy_not_everything_but_match_regexp')
            if not re.match(regex, str(file)):
                self.logger.debug('UnRAR', 'Did not add file {} as it did not match regex "{}".'
                                  .format(str(file), regex))
                return

        self.files.append(file)
        self.watcher_config.append(config)
        try:
            file_info = os.stat(file)
            self.last_size.append(file_info.st_size)
            self.logger.info('Copyer', 'Added {}'.format(file))
        except OSError as e:
            del self.files[len(self.files) - 1]
            del self.watcher_config[len(self.watcher_config) - 1]
            self.logger.error('Copyer', 'Could not find {}, {}'.format(e.filename, e.strerror))

    def check_if_copy_possible(self):
        i = 0
        if len(self.files) > 0:
            self.logger.debug('Copyer', 'Checking if copy is possible for any of the {} files in queue'
                              .format(len(self.files)))
        while i < len(self.files):
            try:
                if self.config.get_config_watcher(self.watcher_config[i], 'copy_actually_dont_do_shit') == 1:
                    result = True
                elif self.config.get_config_watcher(self.watcher_config[i], 'remove_after_finished') == 1:
                    result = self.move_file(i)
                else:
                    result = self.copy_file(i)

                if result:
                    self.notifier.new_notification(self.watcher_config[i])
                    self.logger.new_file(
                        self.config.get_config_watcher(self.watcher_config[i], 'name'),
                        self.files[i],
                        self.config.get_config_watcher(self.watcher_config[i], 'destination_path')
                    )
                    del self.files[i]
                    del self.watcher_config[i]
                    del self.last_size[i]
                    i -= 1  # after deletion the next item is at row i, so (-1+1=0) gives the next element
                else:
                    self.logger.info('Copyer', 'Encountered an error. Will keep trying for file {}'
                                     .format(self.files[i]))

                i += 1
            except OSError as e:  # Error if file does not exist.
                del self.files[i]
                del self.watcher_config[i]
                self.logger.error('Copyer', 'Could not find {}, {}'.format(e.filename, e.strerror))

    def copy_file(self, i):
        if not self.test_permission(self.files[i], 'r'): return True  # Testing read permission
        if not self.test_permission(self.files[i], 'a+'): return False  # Testing write permission
        try:
            self.create_path(i)
            copyfile(self.files[i], self.get_destination(i))
            return True
        except IOError as e:
            self.logger.error('Copyer', 'Encountered error during copying of {}. Error: {}'
                              .format(self.files[i], e))
        return False

    def move_file(self, i):
        if not self.test_permission(self.files[i], 'r'): return True  # Testing read permission
        if not self.test_permission(self.files[i], 'a+'): return False  # Testing write permission
        try:
            self.create_path(i)
            os.rename(self.files[i], self.get_destination(i))
            return True
        except OSError as e:
            self.logger.error('Copyer', 'Encountered error during moving of {}. Error: {}'
                              .format(self.files[i], e))
            return False

    def create_path(self, i):
        sour = self.config.get_config_watcher(self.watcher_config[i], 'source_path')
        dest = self.config.get_config_watcher(self.watcher_config[i], 'destination_path')
        directory = str(self.files[i]).replace(sour, dest).split("/")
        directory = "/".join(directory[0: len(directory) - 1])
        if not os.path.exists(directory):
            os.makedirs(directory)

    def test_permission(self, file, permission):
        try:
            file = open(file, permission)
            file.close()
            return True
        except IOError as ee:
            if permission == 'a+':
                self.logger.error('Copyer', 'Some process is still writing to file {} (error: {})'
                                  .format(file, ee))
            else:
                self.logger.error('Copyer', 'File does not exist {} (error: {})'
                                  .format(file, ee))
            return False

    def get_destination(self, i):
        sour = self.config.get_config_watcher(self.watcher_config[i], 'source_path')
        dest = self.config.get_config_watcher(self.watcher_config[i], 'destination_path')
        if self.config.get_config_watcher(self.watcher_config[i], 'recursive_directory_building_for_new_file') == 1:
            return str(self.files[i]).replace(sour, dest)
        else:
            split_up = str(self.files[i]).split("/")
            return dest + split_up[len(split_up) - 1]


class Copyer(ActualCopyer, metaclass=Singleton):
    pass
