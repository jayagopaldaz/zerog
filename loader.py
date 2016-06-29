#=============================================================================================================================================================#

myname="loader.py"
version="v3.11"

#=============================================================================================================================================================#
from subprocess import call

try:
    import sys
    sys.path.insert(0, '/home/pi/Desktop/')
    import printer
    printer.hello(myname,version)

    while True:
        printer.p("                                                                 Loader === Hi. I'm beginning a new cycle")
        call(['python3','/home/pi/Desktop/update.py'])
except:
    while True:
        call(['python3','/home/pi/Desktop/update.py'])
    pass
    