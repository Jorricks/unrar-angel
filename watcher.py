import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from unrarrer import UnRAR
from copyer import Copyer


class Watcher:
    def __init__(self, logger, config):
        logger.info('Watcher', 'Initiating Watcher')
        self.logger = logger
        self.config = config
        self.UnRARer = UnRAR()
        self.Copyer = Copyer()
        self.observers = []

        # self.observer = Observer()
        # self.directory_to_watch = config.get_watch_path()

    def run(self):
        self.logger.info('Watcher', 'Got a total of {} active watchers'
                         .format(self.config.get_amount_of_active_watchers()))
        for active_watcher in self.config.get_all_active_watchers():
            self.logger.debug('Watcher', 'Creating {} watcher for config {}'
                              .format(active_watcher['copy_or_unrar'], active_watcher['name']))
            if active_watcher['copy_or_unrar'] == "copy":
                event_handler = CopyHandler(self.logger, self.config, self.Copyer, active_watcher['uid'])
            else:
                event_handler = UnrarHandler(self.logger, self.config, self.UnRARer, active_watcher['uid'])

            observer = Observer()
            recursive = (1 == active_watcher['recursive_searching'])
            try:
                observer.schedule(event_handler,
                                  active_watcher['source_path'],
                                  recursive=recursive)
            except OSError as e:
                self.logger.critical('Watcher', 'Received critical error: {}'.format(e))
                return False
            observer.start()
            self.observers.append(observer)
            self.logger.info('Watcher', 'Started watching directory {}'.format(active_watcher['source_path']))

        self.logger.info('Watcher', 'In total {} watcher(s) got started'.format(len(self.observers)))
        # event_handler = Handler(self.logger, self.config)
        # self.observer.schedule(event_handler, self.directory_to_watch, recursive=True)
        # self.observer.start()
        # self.logger.info('Watcher', 'Started watching directory {}'.format(self.directory_to_watch))
        try:
            while True:
                # Check here if we need to restart our watchers.
                if self.config.should_watchers_restart() is True:
                    self.logger.debug('Watcher', 'Watchers will restart')
                    break
                else:
                    self.UnRARer.check_if_unrar_possible()
                    self.Copyer.check_if_copy_possible()
                time.sleep(self.config.get_config_global('update_delay_in_seconds'))
        except:
            for observer in self.observers:
                observer.stop()
                self.logger.info('Watcher', 'Got unexpected result, stopping observer.')

        for observer in self.observers:
            observer.join()
        self.observers.clear()


class UnrarHandler(FileSystemEventHandler):

    def __init__(self, logger, config, unrar, config_uid):
        self.logger = logger
        self.config = config
        self.unrar = unrar
        self.config_uid = config_uid
        logger.debug('Watcher', 'Created a file event unrar handler for config %s' % self.config_uid)

    def on_any_event(self, event, **kwargs):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            self.logger.info('Watcher', 'Received created event: %s' % event.src_path)
            self.unrar.add_new_file(event.src_path, '1')


class CopyHandler(FileSystemEventHandler):

    def __init__(self, logger, config, copyer, config_uid):
        self.logger = logger
        self.config = config
        self.copyer = copyer
        self.config_uid = config_uid
        logger.debug('Watcher', 'Created a file event copy handler for config %s' % self.config_uid)

    def on_any_event(self, event, **kwargs):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            self.logger.info('Watcher', 'Received created event: %s' % event.src_path)
            self.copyer.add_new_file(event.src_path, '1')
