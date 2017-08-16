import os
import pprint

try:
    statinfo = os.stat('somefile.txt')
    print(statinfo.st_size)
except OSError as e:
    print(e.errno)
    print(e.filename)
    print(e.strerror)