# Unrar angel
A light-weight, highly configurable, unrar daemon.

## Dependencies
- [Watchdog](https://pypi.python.org/pypi/watchdog "Watchdog")
- [TinyDB](http://tinydb.readthedocs.io/en/latest/ "TinyDB")
- [Python wrapper for unrar](https://github.com/matiasb/python-unrar "rarfile")
- [RARLAB Unrar library](http://www.rarlab.com/rar_add.htm "RARLAB")
- [Requests](http://docs.python-requests.org/en/master/user/quickstart/ "Requests library documentation")
- [Flask](http://flask.pocoo.org/ "Flask")
- [Advanced logging example](https://docs.python.org/2/howto/logging.html#configuring-logging "Advanced logging example")
- [Plex.tv server commands](https://support.plex.tv/hc/en-us/articles/201638786-Plex-Media-Server-URL-Commands?mobile_site=true "Plex.tv server commands")

## Roadmap
1. Create the Python daemon. Done
2. Create a logger. Done
3. Create a file watcher. Done
4. Create a settings function by using json. Done
5. Create the Unrar function inside the file watcher. Done
6. Create automatically update plex.tv library. Done
7. Create a function to test the installation and the configs. Done
8. Make the unrar script perfect, to support all settings.
9. Create the website to edit the settings.
10. Create testing framework.
11. Add logging to the website.

## Installation instructions
1. Install Python 3.3-3.6 (3.5 preferred)
2. Install the program by installing git after which you execute
```linux
git clone https://github.com/JorricksTU/unrar-angel
```
3. Run the program as specified and use verify_install as param
4. Install watchdog, unrar, tinydb, requests with pip
5. Download the latest RARLAB unrar tarball found
[here](http://www.rarlab.com/rar_add.htm "RARLAB library")
called UnRAR source.
6. Follow the instructions
[here](https://help.ubuntu.com/community/CompilingEasyHowTo "Install unrar lib")
to install the latest rar library (Do not forget to move the tarball to /usr/local/src).
7. Verify if everything is installed now with verify_install again.


```linux
pip3 install watchdog unrar tinydb requests

sudo apt-get install build-essential checkinstall
sudo chown $USER /usr/local/src
sudo chmod u+rwx /usr/local/src
tar -xzvf unrarsrc-5.5.8.tar.gz
cd unrar
make
sudo checkinstall
```

## Run instructions
By using the command 'which Python3.5' you get the path of your python3.
Then the result often shows '/usr/bin/python3.5'. Then run the following
command with your python location.
```linux
/usr/bin/python3.5 /home/user/unrar-angel/angel.py param
```
The params possible are 'start', 'stop', 'restart', 'status' and
'verify_program'.

## UML Diagram
Image:

![alt text](doc/Unrar-angel-diagram.jpg "UML Diagram")


## Special thanks to
- [Sander Marechal for a python daemon implementation](https://gist.github.com/andreif/cbb71b0498589dac93cb "Daemon implementation")
