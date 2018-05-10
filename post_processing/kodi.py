import requests


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class KodiUpdater:
    name = 'Kodi'
    config_param = 'kodi_on_or_off'

    def __init__(self, logger, config):
        self.logger = logger
        self.logger.info('Kodi', 'Initializing Kodi class')
        self.config = config

    def update(self, watcher_uid):
        url = 'http://' + \
              self.config.get_config_watcher(watcher_uid, 'kodi_user') + ':' + \
              self.config.get_config_watcher(watcher_uid, 'kodi_pass') + '@' + \
              self.config.get_config_watcher(watcher_uid, 'kodi_ip_port') + '/jsonrpc'
        payload = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "id": "mybash"}
        requests.post(url, json=payload)
        self.logger.info('Kodi', 'Successful update')


class Kodi(KodiUpdater, metaclass=Singleton):
    pass
