import traceback
import datetime
import os


def print_error_file(e):
    i = 0
    dir = 'errors/'
    if not os.path.exists(dir):
        os.makedirs(dir)

    file_name = dir+'error-{date:%Y-%m-%d %H:%M:%S}-'.format(date=datetime.datetime.now())
    while os.path.isfile(file_name + str(i) + '.txt'):
        i += 1

    with open(file_name + str(i) + '.txt', 'a') as f:
        f.write(str(e))
        f.write(traceback.format_exc())
    return file_name + str(i) + '.txt'
