# -*- coding: utf-8 -*-
#
#
#    RE _ ABSTRACTOR !!!
#
#
import time
import math
import tkinter
#import PIL
import threading
import subprocess
import os
import pygame
#import opc

from tkinter import *
#from PIL import Image, ImageTk
from threading import Thread
#from Adafruit_MAX9744 import MAX9744

numLEDs = 64+12+24
#client = opc.Client('localhost:7890')
OFF=1
ON=0
jack_unplugged=False
jack_plugged_in=False
jack_in_use=False
fade=1
faded_out=False
unfaded=False
    
#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')
#thermo_sensor = '/sys/bus/w1/devices/28-00152c2849ee/w1_slave'
thermoString="I can't feel the temperature right now :/"
fthermo=0

winExists=True
btn_startstop=0
btn_60=0
btn_90=0
btn_custom=0
session_60=True
session_90=False
session_custom=False
filtermode=False
h2o2mode=False

default_before_duration= 0 +  5*60 #seconds
default_fade_duration=   0 +  1*60 #seconds
#efault_ses..._duration= 0 + 60*60 #seconds
default_after_duration=  0 +  3*60 #seconds
default_plo_duration=    0 +  3*60 #seconds
default_phi_duration=    0 + 20*60 #seconds
default_h2o2_duration=  10 +  0*60 #seconds
default_uv_duration=     0 + 20*60 #seconds

custom_before_duration=  0 +  0*5*60 #seconds
custom_fade_duration=    4+0 +  0*1*60 #seconds
custom_session_duration= 1+0 +0*120*60 #seconds
custom_after_duration=   0+0 +  0*3*60 #seconds
custom_plo_duration=     0 +  1*60 #seconds
custom_phi_duration=     0 + 20*60 #seconds
custom_h2o2_duration=   10 +  0*60 #seconds
custom_uv_duration=      0 + 20*60 #seconds

session=False
session_start_time=0

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

#reset pins in case they were left on from program termination
#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(p_plo, GPIO.OUT)
#GPIO.setup(p_phi, GPIO.OUT)
#GPIO.setup(p_h2o2, GPIO.OUT)
#GPIO.setup(p_uv, GPIO.OUT)
#GPIO.setup(p_heater1, GPIO.OUT)
#GPIO.setup(p_heater2, GPIO.OUT)
#GPIO.setup(p_heater3, GPIO.OUT)
#GPIO.setup(p_heater4, GPIO.OUT)
#GPIO.output(p_plo, True)
#GPIO.output(p_phi, True)
#GPIO.output(p_h2o2, True)
#GPIO.output(p_uv, True)
#GPIO.output(p_heater1, True)
#GPIO.output(p_heater2, True)
#GPIO.output(p_heater3, True)
#GPIO.output(p_heater4, True)
#GPIO.cleanup()

#set pins fresh
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(p_plo, GPIO.OUT)
#GPIO.setup(p_phi, GPIO.OUT)
#GPIO.setup(p_h2o2, GPIO.OUT)
#GPIO.setup(p_uv, GPIO.OUT)
#GPIO.setup(p_heater1, GPIO.OUT)
#GPIO.setup(p_heater2, GPIO.OUT)
#GPIO.setup(p_heater3, GPIO.OUT)
#GPIO.setup(p_heater4, GPIO.OUT)
#GPIO.setup(p_thermo, GPIO.IN)
#GPIO.setup(p_audio, GPIO.IN)
#GPIO.setup(p_user, GPIO.IN)
#GPIO.setup(p_alert, GPIO.IN)
#
#GPIO.setup(19, GPIO.OUT)
#GPIO.setup(21, GPIO.OUT)
#GPIO.setup(22, GPIO.OUT)
#GPIO.setup(23, GPIO.OUT)
#GPIO.setup(24, GPIO.OUT)
#GPIO.setup(26, GPIO.OUT)
#
#GPIO.output(19, True)
#GPIO.output(21, True)
#GPIO.output(22, True)
#GPIO.output(23, True)
#GPIO.output(24, True)
#GPIO.output(26, True)

#lights based on gpio_out circuit coming back to gpio_in?
#GPIO.setup(p_user_in, GPIO.IN)
#GPIO.setup(p_alert_in, GPIO.IN)


#--------------------------------------------------------
def switch_startstop():
    global btn_startstop
    global session_start_time
    global session
    if filtermode or h2o2mode: return False
    
    session=not session
    if session:
        btn_startstop["text"]="Stop"
        session_start_time=time.time()
    else:
        btn_startstop["text"]="Start"
        
def switch_60():
    global btn_60
    global btn_90
    global btn_custom
    global session_60
    global session_90
    global session_custom
    session_60=True
    session_90=False
    session_custom=False
    btn_60["text"]="60 - Active"
    btn_90["text"]="90"
    btn_custom["text"]="Custom"
    
def switch_90():
    global btn_60
    global btn_90
    global btn_custom
    global session_60
    global session_90
    global session_custom
    session_60=False
    session_90=True
    session_custom=False
    btn_60["text"]="60"
    btn_90["text"]="90 - Active"
    btn_custom["text"]="Custom"

def switch_custom():
    global btn_60
    global btn_90
    global btn_custom
    global session_60
    global session_90
    global session_custom
    session_60=False
    session_90=False
    session_custom=True
    btn_60["text"]="60"
    btn_90["text"]="90"
    btn_custom["text"]="Custom - Active"

def switch(p):
    if GPIO.input(p): GPIO.output(p, False)
    else: GPIO.output(p, True)

def cleanExit():
    global winExists
    winExists=False

#--------------------------------------------------------
def temperatureThread():
    global thermoString
    global fthermo
    
    while winExists:
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
            thermoString="Temperature: "+str(fthermo)+" °F"
        #time.sleep(.25)
            
#--------------------------------------------------------
def windowThread():
    global btn_startstop
    global btn_60
    global btn_90
    global btn_custom
    global session
    global fthermo
    global OFF
    global ON
    global jack_unplugged
    global jack_plugged_in
    global jack_in_use
    global fade
    global unfaded
    global faded_out
    
    try:
        amp = MAX9744() #amp = MAX9744(busnum=2, address=0x4C)
        amp.set_volume(32)
        noAmp=False
    except Exception:
        noAmp=True
        print("no amp - reabstract")
        pass
    
    win=tkinter.Tk()
    win.title("ZeroG")
    win.protocol("WM_DELETE_WINDOW", cleanExit)
    winW=win.winfo_screenwidth()
    winH=win.winfo_screenheight()
    #win.attributes('-fullscreen', True)
    win.config(cursor='none')
    #win.geometry("%dx%d+0+0" % (800,480)) #(winW, winH))

    #=============
    img=PIL.Image.open("/home/pi/Desktop/splash.jpg")
    img=img.resize((winW, winH), PIL.Image.ANTIALIAS)
    tkimg=ImageTk.PhotoImage(img)

    background_label=Label(win, image=tkimg)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    background_label.image=img

    #dot=PIL.Image.open("/home/pi/Desktop/fadeout.jpg")
    #tkdot=ImageTk.PhotoImage(dot)
    
    #btn_60=Label(win, text="FALSE", width=10, height=20, image=tkdot)

    #=============
    
    def manual_filter():
        global filtermode
        global session
        if session: return False
        filtermode=not filtermode
        if filtermode: btn_filter["text"]="Filter - On"
        else: btn_filter["text"]="Filter"

    def manual_h2o2():
        global h2o2mode
        global session
        if session: return False
        h2o2mode=not h2o2mode
        if h2o2mode: btn_h2o2["text"]="H2O2 - On"
        else: btn_h2o2["text"]="H2O2"

    btn_startstop=Button(win, text="Start"      , command=switch_startstop)
    btn_60       =Button(win, text="60 - Active", command=switch_60)#, image=tkdot)
    btn_90       =Button(win, text="90"         , command=switch_90)
    btn_custom   =Button(win, text="Custom"     , command=switch_custom)
    btn_filter   =Button(win, text="Filter"     , command=manual_filter)
    btn_h2o2     =Button(win, text="H2O2"       , command=manual_h2o2)

    D = IntVar()
    def update_custom():
        global custom_session_duration
        #custom_session_duration=D.get()*60
    spinner=Spinbox(win, command=update_custom, cursor='none', textvariable=D, from_=15, to=15*100, justify=CENTER, increment=15)
    D.set(math.floor(custom_session_duration/60))
    #PW = DoubleVar()
    
    #dimmer = Scale(win, variable=PW, length=280, orient=HORIZONTAL, width=30)
    #PW.set(100)
    L = DoubleVar()
    if not noAmp:
        loud = Scale(win, variable=L, length=240, to=100, orient=HORIZONTAL, width=50)
    else:
        volume = StringVar()
        loud = Label(win, textvariable=volume, font=("Helvetica", 16), fg="white", bg="#2e6f8d") #, relief=RAISED)
        volume.set("I think the amp isn't talking to us :/")    
    L.set(80)

    thermo=StringVar()
    alert=StringVar()
    status = StringVar()
    label_status=Label(win, textvariable=status, font=("Helvetica", 16), fg="white", bg="#2e6f8d") #, relief=RAISED)
    label_thermo=Label(win, textvariable=thermo) #, relief=RAISED)
    label_alert =Label(win, textvariable=alert) #, relief=RAISED)
    
    label_status.place(relx=.5, rely=.5, x=-300, y=120)
    label_thermo.place(relx=.5, rely=.5, x=-300, y=160)
    label_alert.place (relx=.5, rely=.5, x=-300, y=180)
    
    #dimmer.place(relx=.5, rely=.5, x=-300, y=40)
    loud.place  (relx=.5, rely=.5, x=  60, y=10)

    btn_startstop.place(relx=.5, rely=.5, x=200, y=120, width=100, height=70)
    btn_60.place    (relx=.5, rely=.5, x=-300, y=-100, width=100, height=70)
    btn_90.place    (relx=.5, rely=.5, x=-180, y=-100, width=100, height=70)
    spinner.place   (relx=.5, rely=.5, x=-300, y=  10, width=100, height=70)
    btn_custom.place(relx=.5, rely=.5, x=-180, y=  10, width=100, height=70)
    btn_filter.place(relx=.5, rely=.5, x=  80, y=-100, width=100, height=70)
    btn_h2o2.place  (relx=.5, rely=.5, x= 200, y=-100, width=100, height=70)
    userElapse=0+time.time()
    alertElapse=0+time.time()

    lightMode=False
    alertMode=False

    DIM=0
    VOL=0
    fade=1
    
    while winExists:
        win.update()
        try:
            #basic session testing
            if session:
                elapsed=time.time()-session_start_time

                if session_60: float_end=60*60
                if session_90: float_end=90*60
                if session_custom:
                    before_duration=custom_before_duration
                    float_end=custom_session_duration+custom_before_duration
                    fade_duration=custom_fade_duration
                    after_duration=custom_before_duration
                    plo_start=float_end+custom_fade_duration+custom_after_duration
                    phi_start=plo_start+custom_plo_duration
                    h2o2_end=phi_start+custom_h2o2_duration
                    uv_end=phi_start+custom_uv_duration
                    pump_end=phi_start+custom_phi_duration
                else:
                    before_duration=default_before_duration
                    fade_duration=default_fade_duration
                    after_duration=default_after_duration
                    plo_start=float_end+default_fade_duration+default_after_duration
                    phi_start=plo_start+default_plo_duration
                    h2o2_end=phi_start+default_h2o2_duration
                    uv_end=phi_start+default_uv_duration
                    pump_end=phi_start+default_phi_duration

                if elapsed>float_end:
                    fade=(elapsed-float_end)/fade_duration
                elif elapsed>before_duration: fade=1-(elapsed-before_duration)/fade_duration

                if fade<0: fade=0
                if fade>1: fade=1

                #PW.set(fade*100)
                #L.set(fade*100)

                if elapsed>pump_end:
                    session=False
                    fade=1
                    #PW.set(100)
                    #L.set(100)
                    btn_startstop["text"]="Start"
                    statusstring="Ready to float :)"
                    GPIO.output(p_plo, OFF)
                    GPIO.output(p_phi, OFF)
                    GPIO.output(p_h2o2, OFF)
                    GPIO.output(p_uv, OFF)
                    
                elif elapsed>phi_start:
                    GPIO.output(p_plo, OFF)
                    GPIO.output(p_phi, ON)
                    if elapsed>h2o2_end: GPIO.output(p_h2o2, OFF)
                    else: GPIO.output(p_h2o2, ON)
                    if elapsed>uv_end: GPIO.output(p_uv, OFF)
                    else: GPIO.output(p_uv, ON)
                elif elapsed>plo_start:
                    GPIO.output(p_plo, ON)

                t=elapsed-before_duration
                sec=math.floor(t%60)
                min=math.floor(t/60)
                if sec<10: s_sec="0"+str(sec)
                else: s_sec=str(sec)
                statusstring="Your session: "+str(min)+":"+s_sec+" ("+str(math.floor(custom_session_duration/60))+" min)"
                
            elif filtermode or h2o2mode:
                if filtermode:
                    GPIO.output(p_plo, OFF)
                    GPIO.output(p_phi, ON)
                    GPIO.output(p_uv, ON)
                if h2o2mode:
                    GPIO.output(p_h2o2, ON)

            else:
                #PW.set(100)
                #L.set(100)
                fade=1
                GPIO.output(p_plo, OFF)
                GPIO.output(p_phi, OFF)
                GPIO.output(p_h2o2, OFF)
                GPIO.output(p_uv, OFF)
                btn_startstop["text"]="Start"

                statusstring="Ready to float :)"

            #DIM=PW.get()/100
            DIM=fade
            if lightMode:
                DIM=1
            if alertMode:
                DIM=.65+.35*math.sin((time.time()-alertElapse)*3.14)

            color = [ (0,0,0) ] * numLEDs
            def rcol(t,d): return math.floor(255*d*(0.6+.4*math.sin(time.time()*1+t/30*3.14)))
            def gcol(t,d): return math.floor(255*d*0.1)
            def bcol(t,d): return math.floor(255*d*1.0)
            def wcol(t,d): return math.floor(255*d*0.5)

            
            for i in range(0,numLEDs,4):
                #if i >= 64*1000:
                color[i+0]=(rcol(i+0,DIM),gcol(i+0,DIM),bcol(i+0,DIM))
                color[i+1]=(gcol(i+1,DIM),wcol(i+0,DIM),rcol(i+1,DIM))
                color[i+2]=(wcol(i+1,DIM),bcol(i+1,DIM),gcol(i+2,DIM))
                color[i+3]=(bcol(i+2,DIM),rcol(i+2,DIM),wcol(i+2,DIM))
            client.put_pixels(color)   
            
            oldVOL=VOL
            VOL=fade*L.get()/100            
            if oldVOL != VOL:
                if not noAmp:
                    amp.set_volume(math.floor(VOL*63))
                
            #this is the current heater algorithm
            thermo.set(thermoString)
            if fthermo<93.5 and GPIO.input(p_heater1):
                GPIO.output(p_heater1,ON)
                GPIO.output(p_heater2,ON)
                GPIO.output(p_heater3,ON)
                GPIO.output(p_heater4,ON)
            if fthermo>93.5 and not GPIO.input(p_heater1):
                GPIO.output(p_heater1,OFF)
                GPIO.output(p_heater2,OFF)
                GPIO.output(p_heater3,OFF)
                GPIO.output(p_heater4,OFF)
            
            if GPIO.input(p_user) and time.time()-userElapse>.5:
                #print("USER LIGHT TRUE");
                lightMode=True
            if not GPIO.input(p_user):
                userElapse=time.time()
                #print("USER LIGHT FALSE");
                lightMode=False

            if fade==0 and unfaded: unfaded=False
            if fade!=0 and faded_out: faded_out=False
            
            if GPIO.input(p_alert) and time.time()-alertElapse>.5:
                alert.set("Emergency Light On")
                alertMode=True
            if not GPIO.input(p_alert):
                alertElapse=time.time()
                alert.set("Emergency Light Off")
                alertMode=False

            if not GPIO.input(p_audio) and not jack_in_use:
                jack_plugged_in=True
                jack_in_use=True
            elif GPIO.input(p_audio) and jack_in_use:
                jack_unplugged=True
                jack_in_use=False
                
            statusstring=str(GPIO.input(p_audio))+str(GPIO.input(p_user))+str(GPIO.input(p_alert))
            #statusstring=str(fade)
            status.set(statusstring)

        except Exception as error:
            print(error)
            print("reabstract")
            pass
            
    #cleanup on exit
    #light.ChangeDutyCycle(0)
    #light.stop()
    #GPIO.output(p_plo, False)
    #GPIO.output(p_phi, False)
    #GPIO.output(p_h2o2, False)
    #GPIO.output(p_uv, False)
    ##GPIO.output(p_light, False)
    #GPIO.output(p_heater1, False)
    #GPIO.output(p_heater2, False)
    #GPIO.output(p_heater3, False)
    #GPIO.output(p_heater4, False)
    #GPIO.cleanup()
    pygame.mixer.music.stop()
    try:
        amp.set_volume(0)
    except Exception:
        pass
    
    win.destroy()

#--------------------------------------------------------
def musicThread():
    global jack_in_use
    global jack_plugged_in
    global jack_unplugged
    global fade
    global faded_out
    global unfaded
    global winExists
    
    pygame.mixer.init()
    pygame.mixer.music.load("/home/pi/Desktop/default.mp3")

    while winExists:
        pygame.mixer.music.play()
        #print("play")
        while pygame.mixer.music.get_busy() == True:
            if jack_plugged_in or (fade==0 and not faded_out and not jack_in_use):
                #print("pause")
                pygame.mixer.music.pause()
                jack_plugged_in=False
                faded_out=True
                
            if fade!=0 and (jack_unplugged or (not unfaded and not jack_in_use)):
                #print("unpause")
                pygame.mixer.music.unpause()
                jack_unplugged=False
                unfaded=True
                
            continue
        continue
    
#--------------------------------------------------------
if __name__ == '__main__':
    Thread(target = temperatureThread).start()
    Thread(target = windowThread).start()
    Thread(target = musicThread).start()
