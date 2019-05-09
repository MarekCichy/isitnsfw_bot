#!/usr/bin/python
from subprocess import Popen
import sys
import datetime

filename = sys.argv[1]
while True:
    print('\n'+str(datetime.datetime.today())+"\nStarting " + filename)
    p = Popen("python " + filename, shell=True)
    p.wait()