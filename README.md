# Unrar angel
A light-weight, highly configurable, unrar daemon.

## Dependencies
- [Watchdog](https://pypi.python.org/pypi/watchdog "Watchdog")
- [TinyDB](http://tinydb.readthedocs.io/en/latest/ "TinyDB")
- [RarFile](https://rarfile.readthedocs.io/en/latest/ "rarfile")
- [Flask](http://flask.pocoo.org/ "Flask")
- [Advanced logging example](https://docs.python.org/2/howto/logging.html#configuring-logging "Advanced logging example")

## Roadmap
1. Create the Python daemon.
2. Create a logger.
3. Create a file watcher.
4. Create a settings function by using json.
5. Create the Unrar function inside the file watcher.
6. Create the website to edit the settings.
7. Testing framework.
8. Add logging to the website.

## Installation instructions
1. Install Python3.x (3.5 preferred)
2. Install python watchdog
3. Install
```linux
pip3 install watchdog
```

## UML Diagram
Image:

![alt text](doc/Unrar-angel-diagram.jpg "UML Diagram")


## Special thanks to
- [Sander Marechal for a python daemon implementation](https://gist.github.com/andreif/cbb71b0498589dac93cb "Daemon implementation")
-