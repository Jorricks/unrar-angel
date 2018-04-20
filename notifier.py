import error_reporter
from plexupdater import Plexify
import requests


class Notifier:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.plex = Plexify(self.logger, self.config)

    def new_notification(self, watcher_uid):
        if self.config.get_config_watcher(watcher_uid, 'plex_on_or_off') == 1:
            self.logger.info('Notifier', 'Plex is next to be updated now that we had a successful file operation')
            self.plex.update_library(watcher_uid)

        if self.config.get_config_watcher(watcher_uid, 'kodi_on_or_off') == 1:
            self.logger.info('Notifier', 'Kodi is next to be updated now that we had a successful file operation')
            try:
                url = 'http://' + \
                      self.config.get_config_watcher(watcher_uid, 'kodi_user') + ':' + \
                      self.config.get_config_watcher(watcher_uid, 'kodi_pass') + '@' + \
                      self.config.get_config_watcher(watcher_uid, 'kodi_ip_port') + '/jsonrpc'
                payload = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "id": "mybash"}
                requests.post(url, json=payload)
                self.logger.info('Kodi', 'Successful update')
            except requests.exceptions.ConnectionError as e:
                self.logger.error('Notifier', 'Error in updating Kodi. Could not connect')
                error_file = error_reporter.print_error_file(e)
                self.logger.error('Notifier', 'Complete stacktrace can be found in {}'.format(error_file))
