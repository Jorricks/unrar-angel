import requests
from xml.etree import ElementTree


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PlexUpdater:
    def __init__(self, logger, config):
        self.logger = logger
        self.logger.info('Plex', 'Initializing Plexify class')
        self.config = config

    def update_library(self, config_uid):
        library_uid = self.get_library_uid(config_uid)
        if library_uid > 0:
            self.update_library_call(config_uid, str(library_uid))

    def get_library_uid(self, config_uid):
        url = self.url_builder(self.config.get_config_watcher(config_uid, 'plex_ip_port'), '',
                               self.config.get_config_watcher(config_uid, 'plex_token'))
        try:
            response = requests.get(url)
        except:
            self.logger.critical('Plex', 'Could not connect to server. Please check your config.')
            return 0
        if response.status_code != 200:
            if response.status_code == 401:
                self.logger.error('Plex', 'Plex got 401. You entered incorrect credentials.'
                                  .format(response.status_code))
            else:
                self.logger.error('Plex', 'Plex got error code {}.'.format(response.status_code))
            return 0

        tree = ElementTree.fromstring(response.content)
        library_uids = [el.attrib.get('key') for el in tree.findall(
            ".//Directory[@title='" + self.config.get_config_watcher(config_uid, 'plex_library_name') + "']")]
        if len(library_uids) == 0:
            self.logger.error('Plex', 'Could not find library')
            return 0
        return int(library_uids[0])

    def update_library_call(self, config_uid, library_uid):
        url = self.url_builder(self.config.get_config_watcher(config_uid, 'plex_ip_port'),
                               '/' + library_uid + '/refresh',
                               self.config.get_config_watcher(config_uid, 'plex_token'))
        try:
            response = requests.get(url)
        except:
            self.logger.critical('Plex', 'Could not connect to server. Please check your config.')
            return 0
        if response.status_code == 200:
            self.logger.info('Plex', 'Updated library called {}'
                             .format(self.config.get_config_watcher(config_uid, 'plex_library_name')))
        else:
            self.logger.error('Plex', 'Updating failed with http error code: {}'.format(response.status_code))

    @staticmethod
    def url_builder(url, action, token):
        return 'http://' + url + '/library/sections' + action + '?X-Plex-Token=' + token


class Plexify(PlexUpdater, metaclass=Singleton):
    pass
