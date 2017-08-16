class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ActualConfig:
    def __init__(self):
        self.hallo = "Hallo"

    def get_watch_directory(self):
        return '/home/jorricks/Documents/testenvironment'


class Config(ActualConfig, metaclass=Singleton):
    pass

