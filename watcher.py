import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from simplelogger import SimpleLogger
from unrar import UnRAR


class Watcher:
    def __init__(self, logger, config):
        logger.info('Watcher', 'Initiating Watcher')
        self.observer = Observer()
        self.logger = logger
        self.config = config
        self.directory_to_watch = config.get_watch_directory()
        self.UnRARer = UnRAR()

    def run(self):
        event_handler = Handler(self.logger, self.config)
        self.observer.schedule(event_handler, self.directory_to_watch, recursive=True)
        self.observer.start()
        self.logger.info('Watcher', 'Started watching directory {}'.format(self.directory_to_watch))
        try:
            while True:
                # Check here if we need to restart our watchers.
                self.UnRARer.check_if_unrar_possible()
                time.sleep(2)
        except:
            self.observer.stop()
            self.logger.info('Watcher', 'Got unexpected result')

        self.observer.join()


class Handler(FileSystemEventHandler):

    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def on_any_event(self, event, **kwargs):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            unrar = UnRAR()
            unrar.add_new_file_to_unrar(event.src_path, '1')
            logger = SimpleLogger()
            logger.info('Watcher', 'Received created event: %s' % event.src_path)

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            logger = SimpleLogger()
            logger.info('Watcher', 'Received modified event: %s' % event.src_path)
