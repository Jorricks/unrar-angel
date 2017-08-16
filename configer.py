from tinydb import TinyDB, Query
from tinydb.operations import set


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

    def get_all_active_watchers(self):
        setting = Query()
        return self.watchers.search(setting.on_or_off == 1)

    def get_amount_of_active_watchers(self):
        return len(self.get_all_active_watchers())

    def should_watchers_restart(self):
        return self.watchers_should_restart


class Config(ActualConfig, metaclass=Singleton):
    pass
