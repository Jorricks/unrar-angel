from shutil import copyfile, rmtree
from os import remove, mkdir, path
import time

# ##### Config ###### #
good_file = 'goodrar.rar'
bad_file = 'invalidrar.rar'
test_directory = '/home/user/Downloads'
output_directory = '/home/user/Downloads_unrar'
remove_entire_directory = True
# ##### Config ###### #

print('What do you want?\n'
      '1. Copy good_file\n'
      '2. Copy bad_file\n')

file_number = 0
file_name = ''
while not (file_number == 1 or file_number == 2):
    file_number = int(input('Your decision? '))
    if file_number == 1:
        file_name = good_file
    if file_number == 2:
        file_name = bad_file

if remove_entire_directory:
    rmtree(output_directory)
    mkdir(output_directory)

if path.isfile(test_directory+'/'+file_name):
    remove(test_directory+'/'+file_name)
time.sleep(1)
copyfile('files/'+file_name, test_directory+'/'+file_name)
