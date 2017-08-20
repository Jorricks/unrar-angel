import os  # for testing if configs are valid paths.
from tinydb import TinyDB, Query
from tinydb.operations import set
import consoleprint as console


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ActualConfig:
    def __init__(self):
        self.logger = ''
        self.globals = TinyDB('config/global.json')
        self.watchers = TinyDB('config/watchers.json')

        self.test_globals()
        self.test_watchers()

        self.watchers_should_restart = False

    def set_logger(self, logger):
        self.logger = logger

    def search_and_set_globals(self, key, value):
        # A key and value are a different record
        setting = Query()
        if len(self.globals.search(setting.key == key)) == 0:
            self.globals.insert({'key': key, 'value': value})

    def test_globals(self):
        self.search_and_set_globals('personal_name', 'Doe')
        self.search_and_set_globals('program_name', 'UnRAR angel')
        self.search_and_set_globals('logging_path', '/tmp/angel-logger.log')
        self.search_and_set_globals('logging_level', 'DEBUG')
        self.search_and_set_globals('angel_pid_path', '/tmp/unrar-angel.pid')
        self.search_and_set_globals('unrar_check_delay_in_seconds', 2)

    def get_config_global(self, key):
        setting = Query()
        if len(self.globals.search(setting.key == key)) != 0:
            return self.globals.search(setting.key == key)[0]['value']
        else:
            self.logger.critical('Config', 'Invalid global config key requested. {}'.format(key))
            return False

    def search_and_set_watcher(self, key, value):
        # A key and value are on the same record
        setting = Query()
        for item in self.watchers:
            if key not in item:
                self.watchers.update(set(key, value), setting.uid == item['uid'])

    def get_amount_of_watchers(self):
        return len(self.watchers)

    def check_amount_of_watchers(self):
        if len(self.watchers) == 0:
            self.watchers.insert({'uid': 1})

    def test_watchers(self):
        self.check_amount_of_watchers()
        self.search_and_set_watcher('uid', 1)  # D
        self.search_and_set_watcher('on_or_off', 0)  # D
        self.search_and_set_watcher('name', 'Watcher config 1')  # D

        self.search_and_set_watcher('source_path', '/home/user/Downloads')  # D
        self.search_and_set_watcher('destination_path', '/home/user/Downloads_unrar')  # D
        self.search_and_set_watcher('copy_or_unrar', 'unrar')
        self.search_and_set_watcher('remove_after_finished', 0)
        self.search_and_set_watcher('match_all_rar_formats', 1)
        self.search_and_set_watcher('if_not_match_rar_formats_then_regexp', '')

        self.search_and_set_watcher('recursive_searching', 1)  # D
        self.search_and_set_watcher('recursive_directory_building_for_new_file', 1)

        self.search_and_set_watcher('plex_on_or_off', 0)
        self.search_and_set_watcher('plex_ip_port', '127.0.0.1:32400')
        self.search_and_set_watcher('plex_token', '7nr83qpBXvJZsJqbitQD')
        self.search_and_set_watcher('plex_library_name', 'TV Series')

    def add_new_watchers(self):
        self.watchers.insert({'uid': self.get_highest_uid_watcher()+1, 'name': 'Watcher config 2'})

    def copy_watcher(self, uid_original):
        setting = Query()
        item = self.watchers.search(setting.uid == uid_original)[0]
        item['uid'] = self.get_highest_uid_watcher() + 1
        item['on_or_off'] = 0
        item['name'] = 'Copy of ' + item['name']
        self.watchers.insert(item)

    def get_highest_uid_watcher(self):
        highest_uid = 0
        for item in self.watchers:
            highest_uid = max(item['uid'], highest_uid)
        return int(highest_uid)

    def get_config_watcher(self, uid, key):
        setting = Query()
        item = self.watchers.search(setting.uid == int(uid))
        if len(item) == 0:
            self.logger.critical('Config', 'Invalid watcher uid given. {} : {}'.format(uid, key))
        elif key not in item[0]:
            self.logger.critical('Config', 'Invalid watcher config key requested. {} : {}'.format(uid, key))
        else:
            return item[0][key]
        return False  # In any other case

    def get_all_watchers(self):
        return self.watchers

    def get_all_active_watchers(self):
        setting = Query()
        return self.watchers.search(setting.on_or_off == 1)

    def get_amount_of_active_watchers(self):
        return len(self.get_all_active_watchers())

    def should_watchers_restart(self):
        return self.watchers_should_restart

    def test_global_int(self, key):
        if not isinstance(self.get_config_global(key), int):
            console.print_conf_error('Global config has invalid value at {}.\n\tShould be an int'.format(key))

    def test_global_string(self, key):
        if not isinstance(self.get_config_global(key), str):
            console.print_conf_error('Global config has invalid value at {}.\n\tShould be a string'.format(key))

    def test_global_path(self, key):
        self.test_global_string(key)
        path = self.get_config_global(key)
        path_without_file = path.split('/')
        path_without_file = path_without_file[0:len(path_without_file)-1]
        path_without_file = "/".join(path_without_file) + "/"
        if os.access(path_without_file, os.W_OK) is not True:
            console.print_conf_error(
                'Global config has invalid value at {}.\n\tShould be a valid path with write access '
                '(/example/of/link.ext)'.format(key))

    def test_global_or(self, key, values):
        if self.get_config_global(key) not in values:
            console.print_conf_error(
                'Global config has invalid value at {}.\n\tShould be one of the following strings: {}'
                .format(key, ", ".join(str(x) for x in values)))

    @staticmethod
    def test_watcher_boolean(value, key):
        if value != 0 and value != 1:
            console.print_conf_error('Watcher config has invalid value at {}.\n\tShould be 0 for off or 1 for on'
                                     .format(key))

    @staticmethod
    def test_watcher_int(value, key):
        if not isinstance(value, int):
            console.print_conf_error('Watcher config has invalid value at {}.\n\tShould be an integer value'
                                     .format(key))

    @staticmethod
    def test_watcher_str(value, key):
        if not isinstance(value, str):
            console.print_conf_error('Watcher config has invalid value at {}.\n\tShould be a string'.format(key))

    @staticmethod
    def test_watcher_path(value, key):
        if os.access(value, os.W_OK) is not True:
            console.print_conf_error(
                'Watcher config has invalid value at {}.\n\tShould be a valid path with write access'
                .format(key))

    @staticmethod
    def test_watcher_or(value, key, values):
        if value not in values:
            console.print_conf_error(
                'Global config has invalid value at {}.\n\tShould be one of the following strings: {}'
                .format(key, ", ".join(str(x) for x in values)))

    def test_each_individual_setting(self):
        print('Verifying all global settings')
        for gs in ['personal_name', 'program_name']:
            self.test_global_string(gs)

        for gs in ['unrar_check_delay_in_seconds']:
            self.test_global_int(gs)

        for gs in ['logging_path', 'angel_pid_path']:
            self.test_global_path(gs)

        self.test_global_or('logging_level', ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])

        console.print_ok('Verified all global settings')
        print('Verifying all watcher settings')

        uid_list = []
        for watcher in self.get_all_watchers():
            for ws in ['on_or_off', 'remove_after_finished', 'match_all_rar_formats',
                       'recursive_searching', 'recursive_directory_building_for_new_file',
                       'plex_on_or_off']:
                self.test_watcher_boolean(watcher[ws], ws)

            for ws in ['uid']:
                self.test_watcher_int(watcher[ws], ws)
                if watcher[ws] in uid_list:
                    console.print_conf_error('All watchers should have a distinct UID, {} is defined multiple times.'
                                             .format(watcher[ws]))
                uid_list.append(watcher[ws])

            for ws in ['name', 'if_not_match_rar_formats_then_regexp',
                       'plex_ip_port', 'plex_token', 'plex_library_name']:
                self.test_watcher_str(watcher[ws], ws)

            for ws in ['source_path', 'destination_path']:
                self.test_watcher_path(watcher[ws], ws)

            self.test_watcher_or(watcher['copy_or_unrar'], 'copy_or_unrar', ['copy', 'unrar'])

        console.print_ok('Verified all watcher settings')


class Config(ActualConfig, metaclass=Singleton):
    pass
