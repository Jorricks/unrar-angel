# Unrar angel
A light-weight, highly configurable, unrar daemon.

## Dependencies
- [Python Daemon implementation by Sander Marechal](https://gist.github.com/andreif/cbb71b0498589dac93cb "Daemon implementation")
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

## UML Diagram
Image:

![alt text](doc/Unrar-angel-diagram.jpg "UML Diagram")