import atexit
import os
import signal
import sys
import time


class Daemon:
    """A generic daemon class.

    Usage: subclass the daemon class and override the run() method."""

    def __init__(self, pidfile, logger, config):
        self.pidfile = pidfile
        self.logger = logger
        self.config = config
        self.logger.debug('Daemon', 'Initiating Daemon')

    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism."""
        self.logger.info('Daemon', 'Daemonizing')

        self.logger.debug('Daemon', 'Initiating first fork')
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #1 failed: {0}\n'.format(err))
            self.logger.critical('Daemon', 'First fork failed')
            sys.exit(1)

        self.logger.debug('Daemon', 'Decoupling after first fork')
        # decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)

        self.logger.debug('Daemon', 'Initiating second fork')
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #2 failed: {0}\n'.format(err))
            self.logger.critical('Daemon', 'Second fork failed')
            sys.exit(1)

        self.logger.debug('Daemon', 'Redirecting standard output descriptors')
        sys.stdout = Unbuffered(sys.stdout)
        sys.stderr = Unbuffered(sys.stderr)
        si = open(os.devnull, 'r')
        os.dup2(si.fileno(), sys.stdin.fileno())

        self.logger.debug('Daemon', 'Creating PID file')
        atexit.register(self.delpid)

        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as f:
            f.write(pid + '\n')

        self.logger.debug('Daemon', 'Daemon has been started with PID: {}'.format(pid))
        print('Started daemon PID: {}'.format(pid))

    def delpid(self):
        self.logger.debug('Daemon', 'Deleting PID file')
        os.remove(self.pidfile)

    def start(self):
        """Start the daemon."""
        self.logger.debug('Daemon', 'Starting daemon')

        # Check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid:
            print("ERROR - The unrar angle daemon was already found. Daemon already running?")
            self.logger.error('Daemon', 'PID file already exists, exiting')
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.logger.debug('Daemon', 'Starting run')
        self.run()

    def stop(self):
        """Stop the daemon."""

        # Get the pid from the pidfile
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if not pid:
            print("ERROR - The unrar angle daemon was not found. Daemon not running?")
            self.logger.warning('Daemon', 'Daemon appears not to be running')
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                self.logger.warning('Daemon', 'Hit error while stopping daemon')
                print(str(err.args))
                sys.exit(1)
        self.logger.info('Daemon', 'Daemon was stopped')
        print("Daemon was stopped")

    def restart(self):
        """Restart the daemon."""
        self.stop()
        self.start()

    def get_pid(self):
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except (IOError, TypeError):
            pid = None
        return pid

    def run(self):
        """You should override this method when you subclass Daemon.

        It will be called after the process has been daemonized by
        start() or restart()."""
        self.logger.critical('Daemon', 'Wrong method bro')


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, data):
        self.stream.writelines(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)
