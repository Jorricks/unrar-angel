from os import listdir, rename, makedirs
from os.path import isfile, join, exists
import re


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SeriesMoverUpdater:
    name = 'SeriesMover'
    config_param = 'move_into_serie_maps'

    def __init__(self, logger, config):
        self.logger = logger
        self.logger.info('Kodi', 'Initializing Kodi class')
        self.config = config

    def update(self, watcher_uid):
        path = self.config.get_config_watcher(watcher_uid, 'destination_path')

        all_files = [f for f in listdir(path) if isfile(join(path, f))]

        for file in all_files:
            split_up = re.compile("((S|s)(\d)(\d)*(E|e)(\d)(\d)*)").split(file)
            if len(split_up) > 1:
                folder_name = split_up[0].replace(".", " ").rstrip().capitalize()
                print(folder_name)
                if not exists(path + folder_name + "/"):
                    makedirs(path + folder_name + "/")
                rename(path + file, path + folder_name + "/" + file)

        self.logger.info('UnRAR', 'Moved all files into subfolders.')


class SeriesMover(SeriesMoverUpdater, metaclass=Singleton):
    pass
