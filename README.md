# Unrar angel
A light-weight, highly configurable, unrar daemon.

## Dependencies
- [Python Daemon implementation by Sander Marechal](https://gist.github.com/andreif/cbb71b0498589dac93cb "Daemon implementation")
- [Watchdog](https://pypi.python.org/pypi/watchdog "Watchdog")
- [TinyDB](http://tinydb.readthedocs.io/en/latest/ "TinyDB")
- [RarFile](https://rarfile.readthedocs.io/en/latest/ "rarfile")
- [Flask](http://flask.pocoo.org/ "Flask")
- [Advanced logging example](https://docs.python.org/2/howto/logging.html#configuring-logging "Advanced logging example")
- [Plex.tv server commands](https://support.plex.tv/hc/en-us/articles/201638786-Plex-Media-Server-URL-Commands?mobile_site=true "Plex.tv server commands")

## Roadmap
1. Create the Python daemon.
2. Create a logger.
3. Create a file watcher.
4. Create a settings function by using json.
5. Create the Unrar function inside the file watcher.
6. Create automatically update plex.tv library.
7. Create the website to edit the settings.
8. Create testing framework.
9. Add logging to the website.

## UML Diagram
Image:

![alt text](doc/Unrar-angel-diagram.jpg "UML Diagram")
