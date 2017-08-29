import sys


def print_error(error):
    print('\033[91m' + '\tCritical error! ' + error + '\n\033[0m')
    sys.stdout.flush()
    sys.exit(1)


def print_conf_error(error):
    print('\033[91m' + '\tCritical error! ' + error + '\033[0m')
    sys.stdout.flush()


def print_warning(warning):
    print('\033[93m' + '\t' + warning + '\n\033[0m')
    sys.stdout.flush()


def print_ok(message):
    print('\033[92m' + '\t' + message + '\n\033[0m')
    sys.stdout.flush()


def printn(message):
    print(message)
    sys.stdout.flush()