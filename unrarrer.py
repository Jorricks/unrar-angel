import os

from simplelogger import SimpleLogger
from configer import Config
from unrar import rarfile
from unrar import unrarlib
from post_processor import PostProcessor
from os import listdir
from os.path import isfile, join
import re
import error_reporter


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ActualUnRAR:
    def __init__(self):
        self.logger = SimpleLogger()
        self.logger.info('UnRAR', 'Initializing UnRAR class')
        self.config = Config()
        self.post_processor = PostProcessor(self.logger, self.config)
        self.files = []
        self.watcher_config = []
        self.last_size = []
        self.error_count = []

    def add_new_file(self, file, config):
        if self.config.get_config_watcher(config, 'unrar_match_only_rar_extension') == 1:
            if str(file)[-4:] != ".rar":
                self.logger.debug('UnRAR', 'Did not add file {} as it did not match .rar as end file'
                                  .format(str(file)))
                return
        else:
            regex = self.config.get_config_watcher(config, 'unrar_not_rar_but_match_regexp')
            if not re.match(regex, str(file)):
                self.logger.debug('UnRAR', 'Did not add file {} as it did not match regex "{}".'
                                  .format(str(file), regex))
                return

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
            error_file = error_reporter.print_error_file(e)
            self.logger.error('UnRAR', 'Complete stacktrace can be found in {}'.format(error_file))

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
                            self.post_processor.new_processed_file(self.watcher_config[i])
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
                            self.error_count[i] += 1
                            self.logger.info('UnRAR',
                                             'Encountered an error. Will keep trying for file {}'
                                             .format(self.files[i]))
                    else:  # This is to prevent unnecessary unrar attempts.
                        self.last_size[i] = file_info.st_size
                i += 1
            except OSError as e:  # Error if file does not exist.
                del self.files[i]
                del self.watcher_config[i]
                del self.last_size[i]
                del self.error_count[i]
                self.logger.error('UnRAR', 'Could not find {}'.format(e.filename))
                error_file = error_reporter.print_error_file(e)
                self.logger.error('UnRAR', 'Complete stacktrace can be found in {}'.format(error_file))

    def unrar_file(self, i, error_count):
        try:
            try:
                file = open(self.files[i], "a+")
                file.close()
            except IOError as ee:
                self.logger.error('UnRAR', 'Some process is still writing to file {}'.format(self.files[i]))
                error_file = error_reporter.print_error_file(ee)
                self.logger.error('UnRAR', 'Complete stacktrace can be found in {}'.format(error_file))
                return False

            if not rarfile.is_rarfile(self.files[i]):
                if error_count == 0:
                    self.logger.error('UnRAR', 'The following file is not a rarfile (yet): {}'.format(self.files[i]))
            else:
                rar = rarfile.RarFile(self.files[i])
                write_permission_dir, no_write_file = self.all_files_writable_in_directory(i)
                if rar.testrar() is not None:
                    if error_count == 0:
                        self.logger.error('UnRAR', 'Inside the rarfile there is a bad file named : {}'
                                          .format(rar.testrar()))
                elif not write_permission_dir:
                    self.logger.error('UnRAR', 'No write permission for file : {}'
                                      .format(no_write_file))
                else:
                    # Option to only extract certain files.. Future work.
                    if error_count > 0:
                        self.logger.info('UnRAR', 'The following rarfile became complete : {}'
                                         .format(self.files[i]))
                    self.logger.info('UnRAR', 'Started unrarring : {}'.format(self.files[i]))

                    unrar_path = self.get_destination(i)
                    self.logger.debug('UnRAR', 'Destination path : {}'.format(unrar_path))

                    try:
                        rar.extractall(path=unrar_path)
                    except Exception as e:
                        self.logger.error('UnRAR', 'Errors encountered during unrar')
                        error_file = error_reporter.print_error_file(e)
                        self.logger.error('UnRAR', 'Complete stacktrace can be found in {}'.format(error_file))
                        return False

                    self.logger.info('UnRAR', 'Finished unrarring : {}'.format(self.files[i]))
                    return True

        except (rarfile.BadRarFile, unrarlib.UnrarException) as e:
            self.logger.error('UnRAR', 'UNRAR error encountered during unrar')
            error_file = error_reporter.print_error_file(e)
            self.logger.error('UnRAR', 'Error stacktrace can be found in {}'.format(error_file))
        except OSError as e:
            self.logger.error('UnRAR', 'OSError encountered during unrar')
            error_file = error_reporter.print_error_file(e)
            self.logger.error('UnRAR', 'Error stacktrace can be found in {}'.format(error_file))
        return False

    def all_files_writable_in_directory(self, i):
        check_permission = self.config.get_config_watcher(self.watcher_config[i], 'unrar_dir_write_permission')
        if check_permission:
            split_up = str(self.files[i]).split('/')
            my_path = "/".join(split_up[0:len(split_up)-1])
            onlyfiles = [f for f in listdir(my_path) if isfile(join(my_path, f))]
            for file in onlyfiles:
                try:
                    file = open(my_path + '/' + file, "a+")
                    file.close()
                except IOError as e:
                    error_file = error_reporter.print_error_file(e)
                    self.logger.error('UnRAR', 'Complete stacktrace can be found in {}'.format(error_file))
                    return False, file
        return True, ''

    def get_destination(self, i):
        sour = self.config.get_config_watcher(self.watcher_config[i], 'source_path')
        dest = self.config.get_config_watcher(self.watcher_config[i], 'destination_path')
        if self.config.get_config_watcher(self.watcher_config[i], 'recursive_directory_building_for_new_file') == 1:
            split_up = str(self.files[i]).replace(sour, dest).split('/')
            split_up = "/".join(split_up[0:len(split_up)-1])
            return split_up
        else:
            return dest


class UnRAR(ActualUnRAR, metaclass=Singleton):
    pass
