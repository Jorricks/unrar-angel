import collections
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

        if not os.path.exists('config'):
            os.makedirs('config')

        self.globals = TinyDB('config/global.json')
        self.watchers = TinyDB('config/watchers.json')

        self.config_items = ConfigItems()

        self.verify_global_configs_are_present()
        self.verify_watcher_configs_are_present()

        self.watchers_should_restart = False

    def set_logger(self, logger):
        self.logger = logger
        self.logger.info('Config', 'Loaded config from directory {}'.format(os.path.abspath("config/global.json")))

    # Global related items
    # - Setting global settings
    # - Verifying that they are set

    def search_and_set_globals(self, key, value):
        # A key and value are a different record
        setting = Query()
        if len(self.globals.search(setting.key == key)) == 0:
            self.globals.insert({'key': key, 'value': value})

    def verify_global_configs_are_present(self):
        global_items = self.config_items.get_global_config_options()
        for global_item in global_items:
            self.search_and_set_globals(global_item[0], global_item[2])

    def get_all_global_settings(self):
        return self.globals

    def get_config_global(self, key):
        setting = Query()
        if len(self.globals.search(setting.key == key)) != 0:
            return self.globals.search(setting.key == key)[0]['value']
        else:
            self.logger.critical('Config', 'Invalid global config key requested. {}'.format(key))
            return False

    def set_config_global(self, value, keys):
        setting = Query()
        self.globals.update({'value': value}, setting.key == keys)
        print('Should have changed {} to {}'.format(keys, value))
        print('Value now is {}'.format(self.get_config_global(keys)))

    # Watcher settings
    # - Searching and setting settings
    # - Verifying that they are set
    # - Getting the amount of watchers
    # - Copying a watcher
    # - Verifying whether they should restart

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

    def verify_watcher_configs_are_present(self):
        self.check_amount_of_watchers()
        watcher_items = self.config_items.get_watcher_config_options()
        for watcher_item in watcher_items:
            self.search_and_set_watcher(watcher_item[0], watcher_item[2])

    def add_new_watchers(self):
        self.watchers.insert({'uid': self.get_highest_uid_watcher()+1,
                              'name': 'Watcher config' + str(self.get_highest_uid_watcher() + 1)})

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

    def get_watcher_by_uid(self, uid_d):
        setting = Query()
        return self.watchers.search(setting.uid == uid_d)

    def get_all_active_watchers(self):
        setting = Query()
        return self.watchers.search(setting.on_or_off == 1)

    def get_amount_of_active_watchers(self):
        return len(self.get_all_active_watchers())

    def should_watchers_restart(self):
        return self.watchers_should_restart

    def set_config_watcher(self, uid, value, key):
        setting = Query()
        self.watchers.update({key: value}, setting.uid == int(uid))

    # Testing settings
    # - Testing whether the values actually match with the intended value.

    @staticmethod
    def test_global_int(value, key):
        if not isinstance(value, int):
            console.print_conf_error('Global config has invalid value at {}.\n\tShould be an int'.format(key))
            return False
        return True

    @staticmethod
    def test_global_string(value, key):
        if not isinstance(value, str):
            console.print_conf_error('Global config has invalid value at {}.\n\tShould be a string'.format(key))
            return False
        return True

    def test_global_path(self, value, key):
        self.test_global_string(value, key)
        path_without_file = value.split('/')
        path_without_file = path_without_file[0:len(path_without_file)-1]
        path_without_file = "/".join(path_without_file) + "/"
        if os.access(path_without_file, os.W_OK) is not True:
            console.print_conf_error(
                'Global config has invalid value at {}.\n\tShould be a valid path with write access '
                '(/example/of/link.ext)'.format(key))
            return False
        return True

    @staticmethod
    def test_global_or(value, key, values):
        if value not in values:
            console.print_conf_error(
                'Global config has invalid value at {}.\n\tShould be one of the following strings: {}'
                .format(key, ", ".join(str(x) for x in values)))
            return False
        return True

    @staticmethod
    def test_watcher_boolean(value, key):
        if not (value or not value):
            console.print_conf_error('Watcher config has invalid value at {}.\n\tShould be 0 for off or 1 for on'
                                     .format(key))
            return False
        return True

    @staticmethod
    def test_watcher_int(value, key):
        if not isinstance(value, int):
            console.print_conf_error('Watcher config has invalid value at {}.\n\tShould be an integer value'
                                     .format(key))
            return False
        return True

    @staticmethod
    def test_watcher_str(value, key):
        if not isinstance(value, str):
            console.print_conf_error('Watcher config has invalid value at {}.\n\tShould be a string'.format(key))
            return False
        return True

    @staticmethod
    def test_watcher_path(value, key):
        if os.access(value, os.W_OK) is not True:
            console.print_conf_error(
                'Watcher config has invalid value at {}.\n\tShould be a valid path with write access'
                .format(key))
            return False
        return True

    @staticmethod
    def test_watcher_or(value, key, values):
        if value not in values:
            console.print_conf_error(
                'Global config has invalid value at {}.\n\tShould be one of the following strings: {}'
                .format(key, ", ".join(str(x) for x in values)))
            return False
        return True

    # Combining all the tests in one function

    def test_each_individual_setting(self):
        print('Verifying all global settings')

        global_items = self.config_items.get_global_config_options()
        for global_item in global_items:
            if global_item[1] == 'str':
                self.test_global_string(self.get_config_global(global_item[0]), global_item[0])
            if global_item[1] == 'int':
                self.test_global_int(self.get_config_global(global_item[0]), global_item[0])
            if global_item[1] == 'path':
                self.test_global_path(self.get_config_global(global_item[0]), global_item[0])
            if global_item[1] == 'bool':
                self.test_global_or(self.get_config_global(global_item[0]), global_item[0], [0, 1])
            if global_item[1] == 'or':
                if len(global_item) < 4:
                    print('Critical error! OR method does not have selection criteria.')
                self.test_global_or(self.get_config_global(global_item[0]), global_item[0], global_items[3])

        console.print_ok('Verified all global settings')
        print('Verifying all watcher settings')

        uid_list = []
        watcher_items = self.config_items.get_watcher_config_options()
        for watcher in self.get_all_watchers():
            for watcher_item in watcher_items:
                if watcher_item[1] == 'str':
                    self.test_watcher_str(watcher[watcher_item[0]], watcher_item[0])
                if watcher_item[1] == 'int':
                    self.test_watcher_int(watcher[watcher_item[0]], watcher_item[0])
                if watcher_item[1] == 'path':
                    self.test_watcher_path(watcher[watcher_item[0]], watcher_item[0])
                if watcher_item[1] == 'bool':
                    self.test_watcher_boolean(watcher[watcher_item[0]], watcher_item[0])
                if watcher_item[1] == 'or':
                    if len(watcher_item) < 4:
                        print('Critical error! OR method does not have selection criteria.')
                    self.test_watcher_or(watcher[watcher_item[0]], watcher_item[0], watcher_items[3])
                if watcher_item[0] == 'uid':
                    if watcher[watcher_item[0]] in uid_list:
                        console.print_conf_error(
                            'All watchers should have a distinct UID, {} is defined multiple times.'
                            .format(watcher[watcher_item[0]]))
                    uid_list.append(watcher[watcher_item[0]])

        console.print_ok('Verified all watcher settings')

    # Function to convert TinyDB items to JSON.
    def get_all_global_settings_json(self):
        arr = collections.defaultdict(dict)
        i = 0
        for global_set in self.config_items.get_global_config_options():
            arr[i]['name'] = global_set[0]
            arr[i]['type'] = global_set[1]
            arr[i]['default'] = global_set[2]
            if len(global_set) > 3:
                arr[i]['enum'] = global_set[3]
            else:
                arr[i]['enum'] = None
            arr[i]['value'] = self.get_config_global(global_set[0])
            i += 1
        return arr

    def get_all_watcher_settings_json(self, watcher_uid=''):
        arr = collections.defaultdict(dict)
        if watcher_uid == '':
            watchers = self.get_all_watchers()
        else:
            watchers = self.get_watcher_by_uid(int(watcher_uid))
        first = True
        i = 0
        for watcher_setting in self.config_items.get_watcher_config_options():
            setting_key = watcher_setting[0]
            setting_type = watcher_setting[1]
            setting_default = watcher_setting[2]
            setting_enum = watcher_setting[3] if len(watcher_setting) > 3 else None
            for watcher in watchers:
                uid = watcher['uid']
                if first:
                    arr[uid] = collections.defaultdict(dict)
                    first = False
                arr[uid][i] = collections.defaultdict(dict)
                arr[uid][i]['name'] = setting_key
                arr[uid][i]['type'] = setting_type
                arr[uid][i]['default'] = setting_default
                arr[uid][i]['enum'] = setting_enum
                arr[uid][i]['value'] = self.get_config_watcher(watcher['uid'], setting_key)
            i += 1
        return arr

    def get_config_item_type(self, key):
        for setting in self.config_items.get_both_global_config_options():
            if setting[0] == key:
                if len(setting) > 3:
                    return setting[1], setting[3]
                else:
                    return setting[1], None
        return None, None


class Config(ActualConfig, metaclass=Singleton):
    pass


# Containing all the default values and what they are for sort of value.
class ConfigItems:
    def __init__(self):
        self.gci = []  # Global config items
        self.wci = []  # Watcher config items
        
        self.gci.append(['personal_name', 'str', 'Doe'])
        self.gci.append(['program_name', 'str', 'UnRAR angel'])
        self.gci.append(['logging_path', 'path', '/tmp/angel-logger.log'])
        self.gci.append(['logging_path_new_files', 'path', '/tmp/angel-logger-new-files.log'])
        self.gci.append(['logging_level', 'option', 'DEBUG'])
        self.gci[len(self.gci) - 1].append(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        self.gci.append(['angel_pid_path', 'path', '/tmp/unrar-angel.pid'])
        self.gci.append(['update_delay_in_seconds', 'int', 2])
        # @ToDo - Change this to 127.0.0.1
        self.gci.append(['web_config_host_ip', 'str', '192.168.10.129'])
        self.gci.append(['web_config_site_port', 'int', 5000])
        self.gci.append(['web_config_api_port', 'int', 5001])
        self.gci.append(['web_password', 'str', 'unrar_angel'])
        
        self.wci.append(['uid', 'int', 1])  # D
        self.wci.append(['on_or_off', 'bool', 0])  # D
        self.wci.append(['name', 'str', 'Watcher config 1'])  # D
        
        self.wci.append(['source_path', 'path', '/home/user/Downloads/'])  # D
        self.wci.append(['destination_path', 'path', '/home/user/Downloads_unrar/'])  # D
        self.wci.append(['recursive_searching', 'bool', 1])  # D
        self.wci.append(['recursive_directory_building_for_new_file', 'bool', 1])  # D
        self.wci.append(['copy_or_unrar', 'option', 'unrar'])  # D
        self.wci[len(self.wci) - 1].append(['copy', 'unrar'])
        self.wci.append(['remove_after_finished', 'bool', 0])  # D
        self.wci.append(['copy_match_everything', 'bool', 1])
        self.wci.append(['copy_not_everything_but_match_regexp', 'str', '.'])
        self.wci.append(['copy_actually_dont_do_shit', 'bool', 0])

        self.wci.append(['unrar_match_only_rar_extension', 'bool', 1])
        self.wci.append(['unrar_not_rar_but_match_regexp', 'str', '.'])
        
        self.wci.append(['plex_on_or_off', 'bool', 0])  # D
        self.wci.append(['plex_ip_port', 'str', '127.0.0.1:32400'])  # D
        self.wci.append(['plex_token', 'str', '7nr83qpBXvJZsJqbitQD'])  # D
        self.wci.append(['plex_library_name', 'str', 'TV Series'])  # D

    def get_global_config_options(self):
        return self.gci

    def get_watcher_config_options(self):
        return self.wci

    def get_both_global_config_options(self):
        return self.gci + self.wci
