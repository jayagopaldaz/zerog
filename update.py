#=============================================================================================================================================================#

myname="update.py"
version="v3.11"

#=============================================================================================================================================================#
import sys
sys.path.insert(0, '/home/pi/Desktop/')
import printer
printer.hello(myname,version)

import threading
import requests
import time
from threading import Thread
from subprocess import call

ip=printer.ip
baseComplete=False

def baseThread():
    OOO="              "
    printer.p(OOO+"baseThread === checking in...")
    global baseComplete
    
    printer.fileUpdate(ip,"unabstractor.py","unabstractor.py")
    call(['python3','/home/pi/Desktop/unabstractor.py'])
    baseComplete=True
    printer.p(OOO+"baseThread === ...checking out")

def callThread():
    OOO="                            "
    printer.fileUpdate(ip,"cooperate.py","cooperate.py")
    printer.p(OOO+"callThread === about to call cooperate...")
    call(['python3','/home/pi/Desktop/cooperate.py'])
    printer.p(OOO+"callThread === ...checking out")
        
if __name__ == '__main__':
    Thread(target = baseThread).start()
    #Thread(target = callThread).start()
    while not baseComplete:
        callThread()
        time.sleep(3)
    printer.goodbye(myname,version)