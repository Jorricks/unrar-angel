import sys
import consoleprint as console


class VerifyInstallation:
    def __init__(self, config):
        console.printn('Testing all required installations\n')

        self.test_python_version()

        self.test_all_packages()

        self.test_unrar_library()

        self.config = config
        self.test_config()

    @staticmethod
    def test_python_version():
        console.printn('Testing python version.')
        if sys.version_info[0] >= 3:
            console.print_ok('Python version is {}'.format(str(sys.version).replace("\n", " ")))
        else:
            console.print_error('Must be using a Python version of at least 3.2.')

    def test_all_packages(self):
        console.printn('Testing all packages\n')
        self.test_package('watchdog')
        self.test_package('requests')
        self.test_package('tinydb')
        # self.test_package('unrar')

    @staticmethod
    def test_package(package):
        console.printn('Testing for package {}'.format(package))
        try:
            __import__(package)
            console.print_ok('Package found')
        except ImportError:
            console.print_error('Critical error! Package not found')

    @staticmethod
    def test_unrar_library():
        try:
            console.printn('Testing for package unrar')
            __import__('unrar')
            console.print_ok('Package found')
        except ImportError:
            console.print_error('Critical error! Package not found')
        except LookupError:
            console.print_error('Unrar library from RARLAB not found. Please read the installation instructions')
        except:
            console.print_error('Unrar library error. Are you sure this is installed? Check installation instructions')

    def test_config(self):
        console.printn('Testing amount of watchers')
        if self.config.get_amount_of_watchers() > 0:
            console.print_ok('Has {} watchers'.format(self.config.get_amount_of_watchers()))
        else:
            console.print_error('0 watchers found. Created one.')

        console.printn('Verifying that each setting is correct\n')
        self.config.test_each_individual_setting()


