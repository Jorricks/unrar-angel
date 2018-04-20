from os import listdir, rename, makedirs
from os.path import isfile, join, exists
import re
import error_reporter


def move_all_series(config, logger, watcher_config):
    if config.get_config_watcher(watcher_config, 'move_into_serie_maps') == 1:
        path = config.get_config_watcher(watcher_config, 'destination_path')
        try:
            all_files = [f for f in listdir(path) if isfile(join(path, f))]

            for file in all_files:
                split_up = re.compile("((S|s)(\d)(\d)*(E|e)(\d)(\d)*)").split(file)
                if len(split_up) > 1:
                    folder_name = split_up[0].replace(".", " ").rstrip().capitalize()
                    print(folder_name)
                    if not exists(path + folder_name + "/"):
                        makedirs(path + folder_name + "/")
                    rename(path + file, path + folder_name + "/" + file)

            logger.info('UnRAR', 'Moved all files into series folders')
        except Exception as e:
            logger.error('MoveSeries', 'Error during moving')
            error_file = error_reporter.print_error_file(e)
            logger.error('MoveSeries', 'Error stacktrace can be found in {}'.format(error_file))
