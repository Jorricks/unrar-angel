import sys
import consoleprint as console


class VerifyInstallation:
    def __init__(self, config):
        print('Testing all required installations\n')

        self.test_python_version()

        self.test_all_packages()

        self.test_unrar_library()

        self.config = config
        self.test_config()

    @staticmethod
    def test_python_version():
        print('Testing python version.')
        if sys.version_info[0] >= 3:
            console.print_ok('Python version is {}'.format(str(sys.version).replace("\n", " ")))
        else:
            console.print_error('Must be using a Python version of at least 3.2.')

    def test_all_packages(self):
        print('Testing all packages\n')
        self.test_package('watchdog')
        self.test_package('requests')
        self.test_package('tinydb')
        # self.test_package('unrar')

    @staticmethod
    def test_package(package):
        print('Testing for package {}'.format(package))
        try:
            __import__(package)
            console.print_ok('Package found')
        except ImportError:
            console.print_error('Critical error! Package not found')

    @staticmethod
    def test_unrar_library():
        try:
            __import__('unrar')
            console.print_ok('Package found')
        except ImportError:
            console.print_error('Critical error! Package not found')
        except LookupError:
            console.print_error('Unrar library not found. Please read the installation instructions')
        except:
            console.print_error('Unrar library error. Are you sure this is installed? Check installation instructions')

    def test_config(self):
        print('Testing amount of watchers')
        if self.config.get_amount_of_watchers() > 0:
            console.print_ok('Has {} watchers'.format(self.config.get_amount_of_watchers()))
        else:
            console.print_error('0 watchers found. Created one.')

        print('Verifying that all watchers have al settings configured.')
        self.config.test_watchers()
        console.print_ok('Finished verifying')

        print('Verifying that each setting is correct\n')
        self.config.test_each_individual_setting()


