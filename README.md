# Unrar angel
A light-weight, highly configurable, unrar daemon.

## Features
- Program created for linux systems that contain Python3.5
- Light-weight unrar daemon that will automatically process new files in a 'watch' directory.
    - The files can be unrarred
    - The files can copied
    - The files can be moved
- Option to automatically update your Plex.TV library after the file is processed.
- Web interface for easy configuration and information regarding the newest events.
- Open source and all that other stuff.
## How to use
- Follow the installation instructions.
- Follow the run instructions.
- Change the config manually or via web interface(recommended)
    - The web interface is located at localhost:5000
    - The two configs are located into '~/.config/unrar-angel/
- Set the global configuration to your liking.
- Create a watcher and test it with putting a new file inside.
- Check in the log or on the web interface whether the file was found.
- Profit and enjoy!

## Installation instructions
1. Install Python 3.5-3.6 (3.5 preferred)
2. Install the program by installing git after which you execute
```linux
git clone https://github.com/JorricksTU/unrar-angel
```
3. Run the program as specified and use verify_install as param
4. Install watchdog, unrar, tinydb, requests with pip
5. Download the latest RARLAB unrar tarball found
[here](http://www.rarlab.com/rar_add.htm "RARLAB library"), it is called
'UnRAR source'.
6. Follow the instructions
[here](https://help.ubuntu.com/community/CompilingEasyHowTo "Install unrar lib")
to install the latest rar library you just downloaded (Do not forget to move the tarball to /usr/local/src).
7. Verify if everything is installed now with verify_install again.

To make it easy, here are all the specific commands.
```linux
apt-get install git

git clone https://github.com/JorricksTU/unrar-angel
cd unrar-angel

pip3 install watchdog unrar tinydb requests flask-restful

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

## FAQ
1. What if my RAR library is not found? \
If you are 100% certain that you followed the installation instruction completely,
then please look into the directory where you have the library.
Inside there should be a libunrar.so and a libunrar.a.
If this is not the case it seems that your compilation did not go correctly.
2. What if I have a problem.
Please post it here in the repo.
3. Are you still actively supporting this project.
Yes. I hope it can be of use to other people as well so if I can help you, let me know!

## Dependencies
- [Watchdog](https://pypi.python.org/pypi/watchdog "Watchdog")
- [TinyDB](http://tinydb.readthedocs.io/en/latest/ "TinyDB")
- [Python wrapper for unrar](https://github.com/matiasb/python-unrar "rarfile")
- [RARLAB Unrar library](http://www.rarlab.com/rar_add.htm "RARLAB")
- [Requests](http://docs.python-requests.org/en/master/user/quickstart/ "Requests library documentation")
- [Flask](http://flask.pocoo.org/ "Flask")

## Special thanks to
- [Sander Marechal for a python daemon implementation](https://gist.github.com/andreif/cbb71b0498589dac93cb "Daemon implementation")
