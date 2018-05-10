import error_reporter
from post_processing.plex import Plexify
from post_processing.kodi import Kodi


class PostProcessor:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.plex = Plexify(self.logger, self.config)
        self.kodi = Kodi(self.logger, self.config)
        self.class_instances = [self.plex, self.kodi]
        self.class_names = ['Plex', 'Kodi']

    def new_processed_file(self, watcher_uid):
        for class_instance in self.class_instances:
            if self.config.get_config_watcher(watcher_uid, class_instance.config_param) == 1:
                self.logger.info('Notifier', '{} is next to be updated now that we had a successful file operation'
                                 .format(class_instance.name))
                try:
                    class_instance.update(watcher_uid)
                except Exception as e:
                    self.logger.error('Notifier', 'Error in updating {}. Please check your config'
                                      .format(class_instance.name))
                    error_file = error_reporter.print_error_file(e)
                    self.logger.error('Notifier', 'Complete stacktrace can be found in {}'.format(error_file))
