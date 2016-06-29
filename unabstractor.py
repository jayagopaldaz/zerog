# -*- coding: utf-8 -*-
#=============================================================================================================================================================#

myname="unabstractor.py"
version="v3.11"

#=============================================================================================================================================================#
abspath='/home/pi/Desktop/'

import sys
sys.path.insert(0, abspath)
import printer
printer.hello(myname,version)
#printer.silent=True
pdelay=12

import time
import math
import subprocess
import os
import pygame
from threading import Thread
import RPi.GPIO as GPIO
from Adafruit_MAX9744 import MAX9744
import opc
import zerog

client = opc.Client('localhost:7890')

lastPrint=0
numLEDs = 512 #128#+12+24
OFF=1
ON=0
jack_unplugged=False
jack_plugged_in=False
jack_in_use=False
#fade=0
faded_out=False
unfaded=False
lightMode=False
alertMode=False
extraWhite=0
    
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#tester:
try:
    fns = [fn for fn in os.listdir("/sys/bus/w1/devices/")]
    if str(fns[0][:2])=="28": thermoID=str(fns[0])
    else: thermoID=str(fns[1])
    thermo_sensor = '/sys/bus/w1/devices/'+thermoID+'/w1_slave'
except:
    thermo_sensor = ''
    pass

    
printer.p("!!!!!!!!!"+thermo_sensor)

#if printer.myID=='Harmony-DEVI': thermo_sensor = '/sys/bus/w1/devices/28-00152c2849ee/w1_slave'
#if printer.myID=='Portland-DEVI1': thermo_sensor = '/sys/bus/w1/devices/?-?/w1_slave'

#portland??

thermoString="I can't feel the water"
fthermo=0

session_60=True
session_90=False
session_custom=False
filtermode=False
h2o2mode=False

session=False
#session_start_time=0

#relay1
p_heater1=31 #heater1
p_heater2=33 #heater2
p_heater3=35 #heater3
p_heater4=37 #heater4

#relay2
p_plo=18
p_phi=16
p_h2o2=15
p_uv=13

p_user=8 #user light   (gray)
p_alert=10 #emergency light    (purple)
p_thermo=7 #thermo sensor
p_audio=11 #music from jack

nojack=False

if printer.myID=='Harmony-DEVI': nojack=True

#reset pins in case they were left on from program termination
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(p_plo, GPIO.OUT)
GPIO.setup(p_phi, GPIO.OUT)
GPIO.setup(p_h2o2, GPIO.OUT)
GPIO.setup(p_uv, GPIO.OUT)
GPIO.setup(p_heater1, GPIO.OUT)
GPIO.setup(p_heater2, GPIO.OUT)
GPIO.setup(p_heater3, GPIO.OUT)
GPIO.setup(p_heater4, GPIO.OUT)
GPIO.output(p_plo, True)
GPIO.output(p_phi, True)
GPIO.output(p_h2o2, True)
GPIO.output(p_uv, True)
GPIO.output(p_heater1, True)
GPIO.output(p_heater2, True)
GPIO.output(p_heater3, True)
GPIO.output(p_heater4, True)
GPIO.cleanup()

#set pins fresh
GPIO.setmode(GPIO.BOARD)
GPIO.setup(p_plo, GPIO.OUT)
GPIO.setup(p_phi, GPIO.OUT)
GPIO.setup(p_h2o2, GPIO.OUT)
GPIO.setup(p_uv, GPIO.OUT)
GPIO.setup(p_heater1, GPIO.OUT)
GPIO.setup(p_heater2, GPIO.OUT)
GPIO.setup(p_heater3, GPIO.OUT)
GPIO.setup(p_heater4, GPIO.OUT)
GPIO.setup(p_thermo, GPIO.IN)
GPIO.setup(p_audio, GPIO.IN)
GPIO.setup(p_user, GPIO.IN)
GPIO.setup(p_alert, GPIO.IN)

GPIO.setup(19, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

GPIO.output(19, True)
GPIO.output(21, True)
GPIO.output(22, True)
GPIO.output(23, True)
GPIO.output(24, True)
GPIO.output(26, True)


def switch(p):
    if GPIO.input(p): GPIO.output(p, False)
    else: GPIO.output(p, True)

#def cleanExit():
#    global zerog.alive
#    zerog.alive=False

#--------------------------------------------------------
def thermo_calibrate(t):
    a1=90
    a2=95
    b1=90
    b2=95
    
    if printer.myID=='Portland-DEVI1':
        a1=87.4 #DEVI's thermal probe
        a2=88.4
        b1=88.6 #Handheld tester
        b2=89.6
    
    if printer.myID=='Harmony-DEVI': 
        a1=96.0 #DEVI's thermal probe
        a2=96.7
        b1=97.0 #Handheld tester
        b2=97.7
    
    ad=a2-a1
    bd=b2-b1
    
    t=b1+(t-a1)/ad*bd
    
    return math.floor(t*10)/10

def temperatureThread():
    OOO="                                                                                                     "
    printer.p(OOO+"temperatureThread === checking in...")    
    global thermoString
    global fthermo
    
    printer.p(OOO+"temperatureThread === entering circuit...")    
    while zerog.alive:
        try:
            catdata = subprocess.Popen(['cat',thermo_sensor], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out,err = catdata.communicate()
            out_decode = out.decode('utf-8')
            lines = out_decode.split('\n')
            
            #f = open(thermo_sensor, 'r')
            #lines = f.readlines()
            #f.close()

            if lines[0].strip()[-3:] != 'YES':
                return 0
            thermo_output = lines[1].find('t=')
            if thermo_output != -1:
                thermo_string = lines[1].strip()[thermo_output+2:]
                thermo_c = float(thermo_string) / 1000.0
                thermo_f = thermo_c * 9.0 / 5.0 + 32.0
                fthermo=math.floor(thermo_f*10)/10
                #fthermo=thermo_calibrate(thermo_f)
                thermoString=str(thermo_calibrate(fthermo))+" °F"
        except:
            thermoString="I can't feel the water"
            pass
            
#--------------------------------------------------------
def actionThread():
    OOO="         "
    printer.p(OOO+"actionThread === checking in...")    
    global session
    global fthermo
    global jack_unplugged,jack_plugged_in,jack_in_use
    global unfaded,faded_out
    global lastPrint,pdelay
    global lightMode,alertMode
    global extraWhite
    
    try:
        amp = MAX9744() #amp = MAX9744(busnum=2, address=0x4C)
        amp.set_volume(0)
        noAmp=False
    except Exception:
        noAmp=True
        pass
    
    thermo="I can't feel the water"
    alert="No alert, probably"
    status = "Just getting warmed up..."

    DIM=0
    VOL=0
    h12hot=time.time()
    h12cool=time.time()
        
    printer.p(OOO+"actionThread === entering circuit...")    
    while zerog.alive:
        try:
            filtermode=zerog.manualfilter
            h2o2mode=zerog.manualh2o2
            session=zerog.floatInProgress
            custom_session_duration=math.floor(zerog.custom_duration)
            zerog.cur_temp=thermoString
            
            if session:
                if zerog.phase==zerog.PHASE_SHUTOFF:
                    statusstring="Ready to float :)"
                    GPIO.output(p_plo, OFF)
                    GPIO.output(p_phi, OFF)
                    GPIO.output(p_h2o2, OFF)
                    GPIO.output(p_uv, OFF)
                    zerog.phase=zerog.PHASE_NONE
                
                bit1=zerog.phase%10
                bit2=(zerog.phase-bit1)%100
                bit3=zerog.phase-bit1-bit2
                if bit1==zerog.PHASE_PHI:
                    GPIO.output(p_plo, OFF)
                    GPIO.output(p_phi, ON)
                    if bit2==zerog.PHASE_UV: GPIO.output(p_uv, ON)
                    else: GPIO.output(p_uv, OFF)
                    if bit3==zerog.PHASE_H2O2: GPIO.output(p_h2o2, ON)
                    else: GPIO.output(p_h2o2, OFF)
                
                if zerog.phase==zerog.PHASE_PLO: GPIO.output(p_plo, ON)
                
            elif filtermode or h2o2mode:
                if filtermode:
                    GPIO.output(p_plo, OFF)
                    GPIO.output(p_phi, ON)
                    GPIO.output(p_uv, ON)
                else:
                    GPIO.output(p_phi, OFF)
                    GPIO.output(p_uv, OFF)
                if h2o2mode:
                    GPIO.output(p_h2o2, ON)
                else:
                    GPIO.output(p_h2o2, OFF)

            else:
                GPIO.output(p_plo, OFF)
                GPIO.output(p_phi, OFF)
                GPIO.output(p_h2o2, OFF)
                GPIO.output(p_uv, OFF)
                statusstring="Ready to float :)"

            oldVOL=VOL
            VOL=(1-zerog.fade)*zerog.max_vol
            if oldVOL != VOL:
                if not noAmp:
                    ampvol=math.floor(VOL*63)
                    if ampvol<0: ampvol=0
                    if ampvol>63: ampvol=63
                    amp.set_volume(ampvol)

            thermotarg=93.5
            calThermo=thermo_calibrate(fthermo)
  
            topHeatOn=3*60
            topHeatOff=5*60
            if printer.myID=='Harmony-DEVI': 
                topHeatOn=60
                topHeatOff=5*60
            if printer.myID=='Portland-DEVI1': 
                topHeatOn=15
                topHeatOff=4*60
            
            if calThermo<thermotarg and GPIO.input(p_heater1) and time.time()-h12cool>topHeatOn:
                GPIO.output(p_heater1,ON)
                GPIO.output(p_heater2,ON)
                h12hot=time.time()
            if (calThermo>thermotarg or time.time()-h12hot>topHeatOff) and not GPIO.input(p_heater1):
                GPIO.output(p_heater1,OFF)
                GPIO.output(p_heater2,OFF)
                h12cool=time.time()
            
            if calThermo<thermotarg and GPIO.input(p_heater3):
                GPIO.output(p_heater3,ON)
                GPIO.output(p_heater4,ON)
            if calThermo>thermotarg+.5 and not GPIO.input(p_heater3):
                GPIO.output(p_heater3,OFF)
                GPIO.output(p_heater4,OFF)
            
            if GPIO.input(p_user): #and time.time()-userElapse>.5:
                #print("USER LIGHT TRUE");
                zerog.lightMode=True
                lightMode=True
            if not GPIO.input(p_user):
                #userElapse=time.time()
                #print("USER LIGHT FALSE");
                zerog.lightMode=False
                lightMode=False

            if zerog.fade==1 and unfaded: unfaded=False
            if zerog.fade!=1 and faded_out: faded_out=False
            
            if printer.myID!='Portland-DEVI1':
                if GPIO.input(p_alert):
                    #alert.set("Emergency Light On")
                    zerog.alertMode=True
                    alertMode=True
                if not GPIO.input(p_alert):
                    alertElapse=time.time()
                    #alert.set("Emergency Light Off")
                    zerog.alertMode=False
                    alertMode=False
            else: 
                zerog.alertMode=False
                alertMode=False
            
            if not GPIO.input(p_audio) and not jack_in_use:
                jack_plugged_in=True
                jack_in_use=True
            elif GPIO.input(p_audio) and jack_in_use:
                jack_unplugged=True
                jack_in_use=False
            if nojack:
                jack_in_use=False
                jack_plugged_in=False
                
            #zerog.debugstring=statusstring
            
            if time.time()-lastPrint>pdelay: #and zerog.phase>0:
                #pdelay+=.1
                lastPrint=time.time()
                #printer.p("phase: "+str(zerog.phase))
                
                pre=OOO+"actionThread === "
                br="<br>"+pre
                statusstring=pre+"=========================="
                statusstring+=br+"session      : "+str(session)
                statusstring+=br+"min_float    : "+str(zerog.min_float+2*zerog.min_fade)
                statusstring+=br+"temperature  : "+thermoString
                statusstring+=br+"raw temp     : "+str(fthermo)
                statusstring+=br+"times        : "+zerog.timeleft_str
                statusstring+=br+"phase        : "+zerog.dephaser()
                statusstring+="<br>"
                statusstring+=br+"fade         : "+str(math.floor(zerog.fade*100))+"%"
                statusstring+=br+"lightsOkay   : "+str(zerog.lightsOkay)
                statusstring+=br+"extraWhite   : "+str(extraWhite)
                statusstring+="<br>"
                statusstring+=br+"jack_in_use  : "+str(jack_in_use)
                statusstring+=br+"p_user|alert : "+bool_to_on_off(GPIO.input(p_user))+"|"+bool_to_on_off(GPIO.input(p_alert))
                statusstring+=br+"p_heater1234 : "+heaterString()
                statusstring+="<br>"
                statusstring+=br+"man_filter   : "+str(filtermode)
                statusstring+=br+"man_h2o2     : "+str(h2o2mode)
                statusstring+=br+"max_vol      : "+str(math.floor(zerog.max_vol*100))+"%"
                statusstring+=br+"cust_dur     : "+str(custom_session_duration)
                statusstring+="<br>"
                statusstring+=br+"pdelay       : "+str(math.floor(pdelay*10))+"ds"
                printer.p(statusstring)
        except:
            zerog.alive=False

    #cleanup on exit
    GPIO.output(p_plo, False)
    GPIO.output(p_phi, False)
    GPIO.output(p_h2o2, False)
    GPIO.output(p_uv, False)
    GPIO.output(p_heater1, False)
    GPIO.output(p_heater2, False)
    GPIO.output(p_heater3, False)
    GPIO.output(p_heater4, False)
    GPIO.cleanup()
    pygame.mixer.music.stop()
    try:
        global client
        amp.set_volume(0)
        color = [ (0,0,0) ] * numLEDs
        client.put_pixels(color)
    except Exception:
        pass


def bool_to_on_off(b):
    if b: return "ON"
    else: return "OFF"
    
def heaterString():
    h1="OFF"
    h2="OFF"
    h3="OFF"
    h4="OFF"
    if GPIO.input(p_heater1)==ON: h1="ON"
    if GPIO.input(p_heater2)==ON: h2="ON"
    if GPIO.input(p_heater3)==ON: h3="ON"
    if GPIO.input(p_heater4)==ON: h4="ON"
    return h1+"|"+h2+"|"+h3+"|"+h4
    
#--------------------------------------------------------
def lightThread():
    global client
    global extraWhite
            
    OOO="                                                                  "
    printer.p(OOO+"lightThread === checking in...")    
    
    def rcol(t,d): return math.floor(255*d*(0.6+.4*math.sin(time.time()*1+t/30*3.14)))
    def gcol(t,d): return math.floor(255*d*0.1)
    def bcol(t,d): return math.floor(255*d*1.0)
    def wcol(t,d): return math.floor(255*d*0.5)
    LEDzero=False
    while zerog.alive:
        DIM=1-zerog.fade
        
        extraWhite=0
        if lightMode:
            DIM=1
            extraWhite=127
        if alertMode:
            DIM=.65+.35*math.sin((time.time())*3.14)
        
        color = [ (0,0,0) ] * numLEDs
        
        if zerog.lightsOkay or lightMode or alertMode:
            LEDzero=False
            for i in range(0,numLEDs,4):
                wcolAdjusted1=wcol(i+0,DIM)+extraWhite
                wcolAdjusted2=wcol(i+1,DIM)+extraWhite
                wcolAdjusted3=wcol(i+2,DIM)+extraWhite
                if wcolAdjusted1>255: wcolAdjusted1=255
                if wcolAdjusted2>255: wcolAdjusted2=255
                if wcolAdjusted3>255: wcolAdjusted3=255
                
                color[i+0]=(rcol(i+0,DIM),gcol(i+0,DIM),bcol(i+0,DIM))
                color[i+1]=(gcol(i+1,DIM),wcolAdjusted1,rcol(i+1,DIM))
                color[i+2]=(wcolAdjusted2,bcol(i+1,DIM),gcol(i+2,DIM))
                color[i+3]=(bcol(i+2,DIM),rcol(i+2,DIM),wcolAdjusted3)

            client.put_pixels(color)
        
        elif not zerog.lightsOkay and not LEDzero:
            printer.p("darkness")
            client.put_pixels([ (0,0,0) ] * numLEDs)
            LEDzero=True
            
        #if zerog.alertMode: time.sleep(.5)
        #else: time.sleep(3)
        time.sleep(1)
        
                
#--------------------------------------------------------
def musicThread():
    OOO="                                                                                                                         "
    printer.p(OOO+"musicThread === checking in...")    
    global jack_in_use
    global jack_plugged_in
    global jack_unplugged
    #global fade
    global faded_out
    global unfaded
    
    pygame.mixer.init()
    pygame.mixer.music.load(abspath+"default.mp3")

    printer.p(OOO+"musicThread === entering circuit...")    
    while zerog.alive:
        pygame.mixer.music.play()
        #print("play")
        printer.p(OOO+"musicThread === play...")    
        while pygame.mixer.music.get_busy() == True:
            if (jack_plugged_in and not nojack) or (zerog.fade==1 and not faded_out and (not jack_in_use or nojack)):
                printer.p(OOO+"musicThread === pause...")    
                pygame.mixer.music.pause()
                if not nojack: jack_plugged_in=False
                faded_out=True
                
            if zerog.fade!=1 and (jack_unplugged or (not unfaded and not jack_in_use)):
                printer.p(OOO+"musicThread === ...unpause")    
                pygame.mixer.music.unpause()
                jack_unplugged=False
                unfaded=True
                
            continue
        continue
    
#--------------------------------------------------------
if __name__ == '__main__':
    try:
        Thread(target = zerog.zerogAlive).start()
        
        timeout=time.time()
        while not zerog.alive and time.time()-timeout<5: continue
            
        if zerog.alive:
            Thread(target = temperatureThread).start()
            Thread(target = actionThread).start()
            Thread(target = lightThread).start()
            Thread(target = musicThread).start()

        while zerog.alive: continue
        
        pygame.quit()
        printer.goodbye(myname,version)
    except:
        exit(0)
        pass
        
#=============================================================================================================================================================#