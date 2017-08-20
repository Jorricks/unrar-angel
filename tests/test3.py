import requests
from xml.etree import ElementTree


class PlexUpdater:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def update_library(self, config_uid):
        library_uid = self.get_library_uid(config_uid)
        if library_uid > 0:
            return self.update_library_call(config_uid, str(library_uid))

    def get_library_uid(self, config_uid):
        url = self.url_builder('192.168.1.32:32400', '', '7nr83qpBXvJZsJqbitQD')
        # url = self.urlbuilder(self.config.get_config_watcher(config_uid, 'plex_ip_port'), '',
        #                       self.config.get_config_watcher(config_uid, 'plex_token'))

        response = requests.get(url)
        tree = ElementTree.fromstring(response.content)
        library_uids = [el.attrib.get('key') for el in tree.findall(".//Directory[@title='"+"TV Series"+"']")]
        if len(library_uids) == 0:
            print('error')
            return 0
        return int(library_uids[0])

    def update_library_call(self, config_uid, library_uid):
        url = self.url_builder('192.168.1.32:32400', '/' + library_uid + '/refresh', '7nr83qpBXvJZsJqbitQD')
        # url = self.urlbuilder(self.config.get_config_watcher(config_uid, 'plex_ip_port'),
        #                       '/' + library_uid + '/refresh',
        #                       self.config.get_config_watcher(config_uid, 'plex_token'))
        response = requests.get(url)
        if response.status_code == 200:
            print('Success')
        else:
            print('Failed with error code: '+ response.status_code)

    @staticmethod
    def url_builder(url, action, token):
        return 'http://' + url + '/library/sections' + action + '?X-Plex-Token=' + token

plex = PlexUpdater('abc', 'def')
plex.update_library('1')
