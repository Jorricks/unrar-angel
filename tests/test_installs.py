import sys
from pprint import pprint

if sys.version_info[0] < 3:
    raise EnvironmentError("Must be using Python 3")


def test_package(package):
    print('Testing for package {}'.format(package))
    try:
        __import__(package)
        print('\033[92m' + '\tPackage found\n' + '\033[0m')
    except ImportError:
        print('\033[91m' + '\tCritical error! Package not found\n' + '\033[0m')
        sys.exit(1)

test_package('watchdog')
test_package('unrar')
test_package('requests')
test_package('tinydb')
