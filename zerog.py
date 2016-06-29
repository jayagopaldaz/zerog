# -*- coding: utf-8 -*-
#=============================================================================================================================================================#

myname="zerog.py"
version="v3.11"

#=============================================================================================================================================================#
develop=0
debugstring=version
abspath='/home/pi/Desktop/'
if develop==1: abspath='./'#+abspath

import sys
sys.path.insert(0, abspath)
import printer
printer.hello(myname,version)
#printer.silent=True


if develop==1: printer.abspath=abspath


import math
import time
import pygame
from pygame.locals import *

pygame.init()
pygame.display.init()
pygame.display.set_caption("Float Control "+version)
if develop==0: pygame.mouse.set_visible(0)
pygame.font.init()

#clock = pygame.time.Clock()
#FRAMES_PER_SECOND = 0
#deltat = clock.tick(FRAMES_PER_SECOND)
screen=pygame.display.set_mode((800, 500), DOUBLEBUF|NOFRAME|RLEACCEL)
stage=pygame.Surface((800,480))

vOffset=26
max_vol=.65
cur_temp="I can't feel the water"
minAlpha=25
gradalpha=0
gradsurface=False
stepperSpeed=0
fade=1
prog=0
lastPrint=0
floatelapsed=0
status_str="READY"
phase=-1
stopcount=False
lightMode=False
alertMode=False
timeleft_str=""
lightsOkay=False
sleepMode=False

PHASE_NONE   = -1
PHASE_SHOWER = 0
PHASE_FADE1  = 1
PHASE_FLOAT  = 2
PHASE_FADE2  = 3
PHASE_WAIT   = 4
PHASE_PLO    = 5
PHASE_PHI    = 6
PHASE_UV     = 70
PHASE_H2O2   = 800
PHASE_SHUTOFF= -2

floatstart=time.time()
floatInProgress=False
foutTheNewCustomDuration=False
custom_duration=120
max_vol=.65
overrideWarning=False

min_shower=5
min_fade  =1
min_float =58
min_fade  =1
min_wait  =3
min_plo   =3
min_phi   =20
min_uv    =20
min_h2o2  =1/60*10
totalDuration=-1
countdown_num=3

_shower=0
_fade  =0
_float =0
_fade  =0
_wait  =0
_plo   =0
_filter=0

mainscreen        = True
floatscreen       = False
playfloat         = False
maintenancescreen = False
manualfilter      = False
manualh2o2        = False
floatpreset       = -1

#min_float       = float(printer.fin('min_float'))
floatstart      = float(printer.fin('floatstart'))
custom_duration = float(printer.fin('custom_duration'))
floatpreset     = float(printer.fin('floatpreset'))
max_vol         = float(printer.fin('max_vol'))

if printer.fin('floatInProgress')  =="True": floatInProgress  =True
if printer.fin('floatscreen')      =="True": floatscreen      =True
if printer.fin('playfloat')        =="True": playfloat        =True
if printer.fin('maintenancescreen')=="True": maintenancescreen=True
if printer.fin('manualfilter')     =="True": manualfilter     =True
if printer.fin('manualh2o2')       =="True": manualh2o2       =True
reloaded=True
if floatpreset==60: min_float=60-2*min_fade
if floatpreset==90: min_float=90-2*min_fade
if floatpreset==-1: min_float=math.floor(custom_duration)-2*min_fade

if not floatInProgress: lightsOkay=True

#printer.p(str(min_float))
printer.p(str(floatstart))
printer.p(str(custom_duration))
printer.p(str(floatpreset))
printer.p(str(max_vol))

printer.p(str(floatInProgress))
printer.p(str(floatscreen))
printer.p(str(playfloat))
printer.p(str(maintenancescreen))
printer.p(str(manualfilter))
printer.p(str(manualh2o2))


gradBarWidth=780
gradBarHeight=108+5
gradBarLeft=(800-gradBarWidth)/2+5
gradBarTop=210

#================================ LOAD IMAGES ================================
#
bglogo   =pygame.image.load(abspath+'guiassets/bglogo.png').convert()
bg       =pygame.image.load(abspath+'guiassets/bg.png').convert()

tester1  =pygame.image.load(abspath+'guiassets/main/tester.jpg').convert()
nonemin  =pygame.image.load(abspath+'guiassets/main/nonemin.png').convert()
sixtymin =pygame.image.load(abspath+'guiassets/main/60min.png').convert()
ninetymin=pygame.image.load(abspath+'guiassets/main/90min.png').convert()
custommin=pygame.image.load(abspath+'guiassets/main/custommin.png').convert()

tester2  =pygame.image.load(abspath+'guiassets/float/tester.jpg').convert()
play     =pygame.image.load(abspath+'guiassets/float/play.png').convert()
stop     =pygame.image.load(abspath+'guiassets/float/stop.png').convert()

settings =pygame.image.load(abspath+'guiassets/settings/settings.png').convert()
filter   =pygame.image.load(abspath+'guiassets/settings/filter.png').convert()
h2o2     =pygame.image.load(abspath+'guiassets/settings/h2o2.png').convert()
volume   =pygame.image.load(abspath+'guiassets/settings/volume.png').convert()

blackout     =pygame.Surface((800,480)).convert()
amber        =pygame.Surface((800,480)).convert()
phonescreen  =pygame.Surface((800,480)).convert()
progbar      =pygame.Surface((800,10)).convert()
reasonSurface=pygame.Surface((800,480)).convert()                
                
blackout.fill((0,0,0))
amber.fill((255,64,16))

alive=True
touched=False
go=False

oldTarg0=0
oldTarg1=0
oldTarg2=0
layer0=nonemin
layer1=False
layer2=False
layer3=False
layer4=False
start=time.time()
gradalpha=64
alpha0=64
alpha1=64
alpha2=64
alphaStep=5

screens_BEGIN=screens_END=0

sixtymin_button  = pygame.Rect(116, 204-vOffset, 140,140)
ninetymin_button = pygame.Rect(322, 204-vOffset, 140,140)
custommin_button = pygame.Rect(528, 204-vOffset, 140,140)
back_button      = pygame.Rect( 56,  78-vOffset, 76,76)
sleep_button     = pygame.Rect(660,  78-vOffset, 76,76)
play_button      = pygame.Rect(190, 340-vOffset, 94,98)
stop_button      = pygame.Rect(505, 340-vOffset, 94,98)
question_button  = pygame.Rect( 60, 352-vOffset, 76,76)
gear_button      = pygame.Rect(668, 352-vOffset, 76,76)
filter_button    = pygame.Rect(170,  80-vOffset, 160,160)
h2o2_button      = pygame.Rect(460,  80-vOffset, 160,160)
volume_button    = pygame.Rect(170-20, 280-vOffset, 160+30,160)
length_button    = pygame.Rect(400-20, 270-vOffset, 270+40,160)
exit_button      = pygame.Rect(0, 0, 20, 20)

default_font      = pygame.font.Font(abspath+"guiassets/main/kozgoxl.otf",16)
tankname_font     = pygame.font.Font(abspath+"guiassets/main/kozgoxl.otf",54)
status_font       = pygame.font.Font(abspath+"guiassets/main/kozgoxl.otf",30)

introfade1=0
introfade2=0
phonealpha=0

def drawPhoneNumber():
    global phonescreen
    phonenum=tankname_font.render("775            292            0048", 1, (164,154,144))
    pygame.draw.rect(phonescreen, (255,255,255),(0,0,800,480), 0)
    phonescreen.blit(phonenum, (400-phonenum.get_rect().width/2,240-phonenum.get_rect().height/2))

def myPhoneNumber():
    global phonealpha
    a=phonealpha
    if a>255: a=255
    if phonealpha>2000: phonealpha=2000
    phonescreen.set_alpha(a)
    screen.blit(phonescreen, (0,0))
    
def tankname():
    global floatelapsed
    global timeleft_str
    tn="DEVI"
    if printer.myID=='Harmony-DEVI': tn="HARMONY"
    if printer.myID=='Portland-DEVI1': tn="FLOAT ON"
    if printer.myID=='SantaCruz-DEVI1': tn="TANK ONE"
    if printer.myID=='SantaCruz-DEVI2': tn="TANK TWO"
    numletters=len(tn)
    tnFull=tankname_font.render(tn,1,(28,103,114))
    charspacing=9
    tw=tnFull.get_rect().width+charspacing*(numletters-1)
    x=400-tw/2
    for c in tn:
        tnLetter=tankname_font.render(c,1,(1,1,1))
        tnLetter.set_alpha(alpha0)
        stage.blit(tnLetter, (x, 54))
        x+=tnLetter.get_rect().width+charspacing

    f=(min_shower+2*min_fade+min_float)*60-floatelapsed
    if f<0: f=totalDuration*60-floatelapsed
    h=math.floor(f/60/60)
    f-=h*60*60
    m=math.floor(f/60)
    f-=m*60
    s=math.floor(f)
    h_str=str(h)
    m_str=str(m)
    s_str=str(s)
    if m<10: m_str="0"+m_str
    if s<10: s_str="0"+s_str
    #12:04 pm"
    tar=time.localtime( floatstart+totalDuration*60 )
    ampm=" am"
    hb=tar[3]
    if hb>11: ampm=" pm"
    if hb>12: hb-=12
    mb=tar[4]
    mb_str=str(mb)
    if mb<10: mb_str="0"+mb_str
    timeleft_str=h_str+":"+m_str+":"+s_str+" • "+str(hb)+":"+mb_str+ampm
    
    if not floatInProgress: timeleft_str = "READY"
    #!!!!!!!!!!!!!!!!!!!!!!!!
    #timeleft_str="u:"+str(lightMode)+" | a:"+str(alertMode)
    timeleft = default_font.render(timeleft_str,1,(140,140,128))
    timeelapsed = default_font.render(str(math.floor(floatelapsed/60))+"min",1,(140,140,128))
    temperature = default_font.render(cur_temp,1,(140,140,128))
    
    
    timeelapsed.set_alpha(alpha0)
    temperature.set_alpha(alpha0)
    stage.blit(timeleft, (400-tw/2, 108))
    stage.blit(temperature, (400+tw/2-temperature.get_rect().width, 108))
    if floatInProgress and floatscreen and not maintenancescreen:
        tx=prog-timeelapsed.get_rect().width/2
        if tx<gradBarLeft+10: tx=gradBarLeft+10
        stage.blit(timeelapsed, (tx,gradBarTop+gradBarHeight+20-vOffset-timeelapsed.get_rect().height))

def statusbar(text):
    status=status_font.render(text,1,(28,103,124))
    status.set_alpha(alpha0)
    stage.blit(status, (400-status.get_rect().width/2, 374-vOffset))

def floatlengthbar(text):
    #print(text)
    floatlength=tankname_font.render(text,1,(28,103,124))
    floatlength.set_alpha(alpha0)
    stage.blit(floatlength, (540-floatlength.get_rect().width/2, 310-vOffset))        

def gradbar():
    if gradsurface: 
        gradsurface.set_alpha(math.floor(.65*gradalpha*alpha0/255)) # 65% grad bar... remember ;) ?
        stage.blit(gradsurface, (gradBarLeft, gradBarTop-vOffset))
        
    m1 = default_font.render("5min",1,(140,140,128))
    m2 = default_font.render(str(math.floor(min_float+min_shower+2*min_fade))+"min",1,(140,140,128))
    stage.blit(m1, (gradBarLeft+_shower, gradBarTop-20-vOffset))
    stage.blit(m2, (gradBarLeft+_shower+2*_fade+_float-m2.get_rect().width, gradBarTop-20-vOffset))
    
def drawgradbar():
    global gradsurface
    global progbar
    global gradalpha
    global gradBarWidth
    global gradBarHeight
    global _shower,_fade,_float,_wait,_plo,_filter
    global totalDuration
    gradalpha=minAlpha
    
    h=gradBarHeight
    w=gradBarWidth
    _r=0
    _g=0
    _b=0

    totalDuration=min_shower+min_fade+min_float+min_fade+min_wait+min_plo+min_phi
    _shower =w/totalDuration*min_shower
    _fade   =w/totalDuration*min_fade
    _float  =w/totalDuration*min_float
    #fade...=               *min_fade
    _wait   =w/totalDuration*min_wait
    _plo    =w/totalDuration*min_plo
    _filter =w/totalDuration*min_phi

    gradsurface = pygame.Surface((w,h))
    progbar     = pygame.Surface((w,h))
    progbar.fill((222,227,233))
    progbar.set_alpha(math.floor(255*.7)) # 70% white prog bar... remember ;) ?
    #gradsurface.set_alpha(math.floor(.65*255)) # 65% grad bar... remember ;) ?
    for x in range(0,799):            
        #try:
        if True:
            #THE GRADIENT
            if x<_shower:                                           _r=_g=_b=255#math.floor(255-    (x         )   /_shower*255)
            if x>_shower and x<_shower+_fade:                       _r=_g=_b=   math.floor(255-   (x-_shower     )    /_fade*255)
            if x>_shower+_fade and x<_shower+_fade+_float:          _r=_g=_b=0#math.floor(255-  (x-_shower-_fade   )     /_float*255)
            if x>_shower+_fade+_float and x<_shower+2*_fade+_float: _r=_g=_b= math.floor( 0 + (x-_shower-_fade-_float)      /_fade*255)
            if x>_shower+2*_fade+_float+_wait:      
                _r= math.floor(255-(x-_shower-2*_fade-_float  ) /_filter*255 *4)
                _g= math.floor(255-(x-_shower-2*_fade-_float  ) /_filter*255 *3)
                _b= math.floor(255-(x-_shower-2*_fade-_float  ) /_filter*255 *2)
                if _r<0: _r=0
                if _g<0: _g=0
                if _b<0: _b=0
                _r+=math.floor( 0 +(x-_shower-2*_fade-_float  ) / _filter*255)
                _b+=math.floor( 0 +(x-_shower-2*_fade-_float  ) / _filter*255)
                if _r>255: _r=255
                if _g>255: _g=255
                if _b>255: _b=255
                
            pygame.draw.line(gradsurface, (_r,_g,_b), (x,0),(x,h), 1)

drawPhoneNumber()
reason=status_font.render("Are both override switches set to OFF?", 1, (194,184,174))
reasonSurface.blit(reason,(400-reason.get_rect().width/2,240-reason.get_rect().height/2))

def zerogAlive():
    global debugstring
    global alive,touched,go
    global introfade1,introfade2
    global layer0,layer1,layer2,layer3,layer4
    global floatscreen,maintenancescreen,playfloat,prog
    global phonealpha,alpha0,alpha1,alpha2,alpha3,alpha4,gradalpha
    global lastPrint,reloaded,stepperSpeed
    global min_float,max_vol,lightsOkay,sleepMode
    global manualfilter,manualh2o2,overrideWarning
    global custom_duration, countdown_num, stopcount, foutTheNewCustomDuration
    global floatpreset,floatInProgress,floatelapsed,floatstart,fade,status_str,phase
    
    OOO="               "
    printer.p(OOO+"zerogAlive === checking in...")    
    if develop==1: printer.p(OOO+"zerogAlive === Set to Develop mode...")    

    printer.p(OOO+"zerogAlive === entering circuit...")    
    lastTick=time.time()
    
    am=1
    pygame.mouse.set_pos(799,479)
    while alive:
        #clock.tick(30)
        am=                             am*.9        +         .1*(time.time()-lastTick)/(1/30)
        am=                             am*.9        +         .1*(time.time()-lastTick)/(1/30)
        fm=am*2
        lastTick=time.time()
        for event in pygame.event.get(): continue
        
        #if time.time()-start>6*60*60 and not floatInProgress: alive=False #autorestart
        #elif time.time()-start<2:
        if time.time()-start<2:
            bglogo.set_alpha(introfade1)
            introfade1+=10*fm
            if introfade1>255: introfade1=255
            screen.blit(bglogo,(0,-vOffset))
            pygame.display.update()

        elif time.time()-start<4:
            bg.set_alpha(introfade2)
            introfade2+=10*fm
            if introfade2>255: introfade2=255
            screen.blit(bg,(0,-vOffset)) #yOffset
            pygame.display.update()
            
        else:
            #mouse position and button clicking
            pos = pygame.mouse.get_pos()
            (mouseL,mouseM,mouseR) = pygame.mouse.get_pressed()
            if mouseL==1 and not touched: touched=True
            if mouseL!=1   and   touched:
                go=True
                touched=False
            else: go=False
                
            #if not touched: mouseL=1
            #go = not mouseL and touched
            
            
            #=== CHECK IF THE MOUSE IS OVER ANY TARGET ZONES ===
            #
            on_exit      =      exit_button.collidepoint(pos)
            on_sixtymin  =  sixtymin_button.collidepoint(pos)
            on_ninetymin = ninetymin_button.collidepoint(pos)
            on_custommin = custommin_button.collidepoint(pos)
            #n_nonemin...
            on_back      =     back_button.collidepoint(pos)
            on_sleep     =    sleep_button.collidepoint(pos)
            on_play      =     play_button.collidepoint(pos)
            on_stop      =     stop_button.collidepoint(pos)
            on_question  = question_button.collidepoint(pos)
            on_gear      =     gear_button.collidepoint(pos)
            on_filter    =   filter_button.collidepoint(pos)
            on_h2o2      =     h2o2_button.collidepoint(pos)
            on_volume    =   volume_button.collidepoint(pos)
            on_length    =   length_button.collidepoint(pos)
            
            
            #printer.p(OOO+"zerogAlive === about to go into the buttons...")
            oldTarg0 = layer0
            oldTarg1 = layer1
            oldTarg2 = layer2
            oldTarg3 = layer3
            oldTarg4 = layer4

            #================== BUTTON AND SCREEN BRANCHING FLOW CHART ==================
            #
            screens_BEGIN=mainscreen+2*floatscreen+4*maintenancescreen
            if mainscreen:
                layer0=nonemin
                if floatpreset==60: layer0 = sixtymin
                if floatpreset==90: layer0 = ninetymin
                if floatpreset==-1: layer0 = custommin
                if on_sixtymin    : layer0 = sixtymin
                if on_ninetymin   : layer0 = ninetymin
                if on_custommin   : layer0 = custommin
                
                if      on_exit and go: alive = False
                if      on_exit and go: printer.p(OOO+"zerogAlive === ending...")
                
                if not floatscreen and not maintenancescreen:
                    if  on_sixtymin and go: floatpreset=60
                    if on_ninetymin and go: floatpreset=90
                    if on_custommin and go: floatpreset=-1
                    #if on_custommin and go: printer.fout('custom_duration',str(custom_duration))
                    
                    if (on_sixtymin or on_ninetymin or on_custommin) and go: 
                        floatscreen = True
                        if floatpreset==-1: min_float = math.floor(custom_duration)-2*min_fade
                        else: min_float = floatpreset-2*min_fade
                        #printer.fout('min_float',str(min_float))
                        printer.fout('floatpreset',str(floatpreset))
                        printer.fout('floatscreen',str(floatscreen))
                
                if on_gear and go: 
                    maintenancescreen=True
                    printer.fout('maintenancescreen',str(maintenancescreen))
                    if manualfilter: layer1=filter
                    if manualh2o2: layer2=h2o2
                
                if floatscreen and not maintenancescreen:
                    if on_back and go: 
                        floatscreen=False
                        printer.fout('floatscreen',str(floatscreen))
                    layer0=play
                 
                    if not manualfilter and not manualh2o2:
                        if on_play and go: prog=0
                        if on_play and go: floatstart=time.time()
                        if on_play and go: floatInProgress=True
                        if on_play and go: printer.fout('floatstart',str(floatstart))
                        if on_play and go: printer.fout('floatInProgress',str(floatInProgress))
                        
                        if on_play and go: playfloat=True 
                        if on_play and go: printer.fout('playfloat',str(playfloat))
                        if on_stop and mouseL:
                            stopcount=True
                            countdown_num=3-(time.time()-countdownstart)
                            if countdown_num<0:
                                playfloat=False
                                printer.fout('playfloat',str(playfloat))
                                printer.fout('floatInProgress',str(floatInProgress))
                                countdown_num=0
                                stopcount=False
                                
                        else: 
                            stopcount=False
                            countdown_num=3
                            countdownstart=time.time()
                    
                    else:    
                        if on_play and go: overrideWarning=time.time()
                        #else: overrideWarning=False
               
                    if playfloat:
                        layer0=stop
                        prog=math.floor(floatelapsed/60/totalDuration*gradBarWidth)
                        
                if maintenancescreen:
                    layer0=settings
                    if on_back and go: printer.fout('custom_duration',str(custom_duration))
                    if on_back and go: printer.fout('max_vol',str(max_vol))
                    if on_back and go: layer0=layer1=layer2=layer3=layer4=0
                    if on_back and go: 
                        maintenancescreen=False
                        printer.fout('maintenancescreen',str(maintenancescreen))
                    
                    #if floatInProgress and phase==4
                    if on_sleep and go: sleepMode=not sleepMode
                        
                    if not floatInProgress:
                        if on_filter and go: manualfilter = not manualfilter
                        if on_filter and go: printer.fout('manualfilter',str(manualfilter))
                        if on_filter and go   and   manualfilter: layer1 = filter
                        if on_filter and go and not manualfilter: layer1 = 0
                        
                        if on_h2o2 and go: manualh2o2 = not manualh2o2
                        if on_h2o2 and go: printer.fout('manualh2o2',str(manualh2o2))
                        if on_h2o2 and go   and   manualh2o2: layer2 = h2o2
                        if on_h2o2 and go and not manualh2o2: layer2 = 0
                    
                    if on_volume and mouseL: 
                        max_vol=(pos[0]-10-volume_button.left) / volume_button.width
                        if max_vol<0: max_vol=0
                        if max_vol>1: max_vol=1
                    
                    if on_length and mouseL:
                        stepper=(pos[0]-length_button.left) / length_button.width - .5
                        
                        if stepper<0 and stepperSpeed==0: custom_duration-=1
                        if stepper>0 and stepperSpeed==0: custom_duration+=1
                        
                        if stepper<0: custom_duration-=stepperSpeed*fm
                        if stepper>0: custom_duration+=stepperSpeed*fm
                        
                        if  stepperSpeed<.5: stepperSpeed+=.001*fm
                        elif stepperSpeed<2: stepperSpeed*=1.1
                        
                        if custom_duration<2*min_fade: custom_duration=2*min_fade
                        if custom_duration>999.9: custom_duration=999
                        
                        #if floatpreset!=60 and floatpreset!=90: 
                        floatpreset=math.floor(custom_duration)
                        foutTheNewCustomDuration=True
                        
                    elif foutTheNewCustomDuration:
                        printer.fout('custom_duration',str(custom_duration))
                        foutTheNewCustomDuration=False
                    else: 
                        stepperSpeed=0
                    
            screens_END=mainscreen+2*floatscreen+4*maintenancescreen
            if screens_BEGIN!=screens_END and floatscreen or reloaded: drawgradbar()
            if reloaded: reloaded=False
            
            if oldTarg0!=layer0: alpha0=minAlpha
            if oldTarg1!=layer1: alpha1=minAlpha
            if oldTarg2!=layer2: alpha2=minAlpha
            if oldTarg3!=layer3: alpha3=minAlpha
            
            if on_question and mouseL and not maintenancescreen and not floatscreen: phonealpha+=alphaStep*fm
            elif phonealpha>0: phonealpha-=alphaStep*fm
            if phonealpha<0: phonealpha=0
            
            
            alpha0+=alphaStep*fm
            alpha1+=alphaStep*fm
            alpha2+=alphaStep*fm
            gradalpha+=alphaStep*fm
            
            if alpha0>255: alpha0=255
            if alpha1>255: alpha1=255
            if alpha2>255: alpha2=255
            if gradalpha>255: gradalpha=255
            
            if layer0: layer0.set_alpha(alpha0)
            if layer1: layer1.set_alpha(alpha1)
            if layer2: layer2.set_alpha(alpha2)
            
            if layer0: stage.blit(layer0,(0,0))
            if layer1: stage.blit(layer1,(153,42))
            if layer2: stage.blit(layer2,(422,42))
            
            if maintenancescreen:
                for x in range(0,6):
                    a=0
                    if max_vol>x/6: a=255
                    elif max_vol>(x-.75)/6: a=64
                    elif max_vol>(x-.50)/6: a=128
                    elif max_vol>(x-.25)/6: a=192
                    volume.set_alpha(math.floor(a))
                    stage.blit(volume,(174+x*26,316))
                
                floatlengthbar(str(math.floor(custom_duration)))
                        
            if not maintenancescreen: 
                tankname()
                if floatscreen:
                    gradbar()
                    statusbar(status_str)
                    if playfloat:
                        #screen.blit(progbar,(gradBarLeft-gradBarWidth+prog,gradBarTop-vOffset))
                        progbar.set_alpha(alpha0*.7)
                        stage.blit(progbar,(gradBarLeft-gradBarWidth+prog,gradBarTop-vOffset))
                        #playfloat: 
                        #if 
                        #else: 
                        #playBAK.blit(progbar,(gradBarLeft-gradBarWidth+prog,gradBarTop-vOffset))
        
                        x=gradBarLeft+prog
                        pygame.draw.line(screen, (0,255,0), (x,gradBarTop-vOffset),(x,gradBarTop+gradBarHeight-vOffset-1), 1)

            screen.blit(stage,(0,0))
            tfade=1
            tlights=False
            if floatInProgress:
                tfade=0
                tlights=True
                phase=PHASE_SHOWER
                status_str="SHOWER"
                
                if floatelapsed/60>min_shower:
                    phase=PHASE_FADE1
                    status_str="FADE"
                    tfade=(floatelapsed/60-min_shower)/min_fade
                    if tfade>1: tfade=1
                
                if floatelapsed/60>min_shower+min_fade: 
                    tlights=False
                    phase=PHASE_FLOAT
                    status_str="FLOAT"
                
                if floatelapsed/60>min_shower+min_fade+min_float:
                    tlights=True
                    phase=PHASE_FADE2
                    status_str="FADE"
                    tfade=1-(floatelapsed/60-(min_shower+min_fade+min_float))/min_fade
                    if tfade<0: tfade=0
                
                if floatelapsed/60>min_shower+2*min_fade+min_float: 
                    phase=PHASE_WAIT
                    status_str="SHOWER"
                    
                if floatelapsed/60>min_shower+2*min_fade+min_float+min_wait: 
                    phase=PHASE_PLO
                    status_str="FILTER"
                
                if floatelapsed/60>min_shower+2*min_fade+min_float+min_wait+min_plo: 
                    phase=PHASE_PHI
                    if floatelapsed/60<min_shower+2*min_fade+min_float+min_wait+min_plo+min_uv: phase+=PHASE_UV
                    if floatelapsed/60<min_shower+2*min_fade+min_float+min_wait+min_plo+min_h2o2: phase+=PHASE_H2O2
                
                if tfade>0:
                    blackout.set_alpha(tfade*192)
                    screen.blit(blackout,(0,0))
                    #if floatscreen and not maintenancescreen: screen.blit(blackout,(0,0))
                
                if floatelapsed/60>totalDuration:
                    playfloat=False
                    floatInProgress=False
                    phase=PHASE_SHUTOFF
                    printer.fout('playfloat',str(playfloat))
                    printer.fout('floatInProgress',str(floatInProgress))
                                                    
            else:
                tlights=True
                phase=PHASE_NONE
                status_str="READY"
                tfade=fade
                if tfade>0: tfade-=.01
                if tfade<0: tfade=0
            #set the actual fade just once! otherwise every so often the other thread will call on it before it is prepared ;)
            
            if not playfloat: floatInProgress=False
            if not floatInProgress: floatstart=time.time()
            if phonealpha>0: myPhoneNumber()
            if stopcount:
                blackout.set_alpha(192)# -(255-alpha0)/255*fade)
                countdown=tankname_font.render(str(math.floor(countdown_num+1)), 1, (164,154,144))
                screen.blit(blackout,(0,0))
                screen.blit(countdown, (400-countdown.get_rect().width/2,240-countdown.get_rect().height/2))

            if overrideWarning!=False:
                th=(time.time()-overrideWarning)/2*3.14
                if th>2*3.14: overrideWarning=False
                a=(.5-math.cos(th)/2)*192
                print(str(th))
                reasonSurface.set_alpha(a)
                screen.blit(reasonSurface, (0,0))
        
            #if lightMode:
            #    #tfade=0
            #    
            #if alertMode:
            #    #tfade=.5+.5*math.sin((time.time()/3)*3.14)
            #    #amber.set_alpha(DIM*255)
            #    #screen.blit(amber,(0,0))
            
            if sleepMode:
                #tlights=False
                if tfade<1: tfade+=.1
                if tfade>1: tfade=1
                blackout.set_alpha(128)
                screen.blit(blackout,(0,0))
            
            lightsOkay=tlights
            fade=tfade
                        
            #floatelapsed=(time.time()-floatstart)*10+60*min_shower
            #floatelapsed=(time.time()-floatstart)*1+60*(min_shower-20/60)
            #floatelapsed=(time.time()-floatstart)*20+60*(min_shower+1*min_fade)
            #floatelapsed=(time.time()-floatstart)*20+60*(min_shower+1*min_fade+min_float)
            #floatelapsed=(time.time()-floatstart)*20+60*(min_shower+2*min_fade+min_float)
            #floatelapsed=(time.time()-floatstart)*20+60*(min_shower+2*min_fade+min_float+min_wait-1)
            #floatelapsed=(time.time()-floatstart)*20+60*(min_shower+2*min_fade+min_float+min_wait+min_plo)
            #floatelapsed=(time.time()-floatstart)*40
        
            #================ ================ ================ ================ ================ 
            floatelapsed=(time.time()-floatstart)   #this is the not-testing-for one
            #================ ================ ================ ================ ================ 
            
            #debug = default_font.render(debugstring,1,(190,190,178))
            #screen.blit(debug, (565, 400))
            
            #================ ACTUALLY DRAW TARGET ZONES FOR TESTING ======================
            #
            #sixtymin_buttonTARG  = pygame.draw.rect(screen, (100,0,0),sixtymin_button, 2)
            #ninetymin_buttonTARG = pygame.draw.rect(screen, (0,100,0),ninetymin_button, 2)
            #custommin_buttonTARG = pygame.draw.rect(screen, (0,0,100),custommin_button, 2)
            #back_buttonTARG      = pygame.draw.rect(screen, (0,0,100),back_button, 2)
            #sleep_buttonTARG     = pygame.draw.rect(screen, (0,0,100),sleep_button, 2)
            #play_buttonTARG      = pygame.draw.rect(screen, (0,100,0),play_button, 2)
            #stop_buttonTARG      = pygame.draw.rect(screen, (100,0,0),stop_button, 2)
            #question_buttonTARG  = pygame.draw.rect(screen, (0,100,0),question_button, 2)
            #gear_buttonTARG      = pygame.draw.rect(screen, (100,0,0),gear_button, 2)
            #filter_buttonTARG    = pygame.draw.rect(screen, (0,100,0),filter_button, 2)
            #h2o2_buttonTARG      = pygame.draw.rect(screen, (0,0,100),h2o2_button, 2)
            #volume_buttonTARG    = pygame.draw.rect(screen, (0,0,100),volume_button, 2)
            #length_buttonTARG    = pygame.draw.rect(screen, (0,100,0),length_button, 2)
            #exit_buttonTARG      = pygame.draw.rect(screen, (0, 0, 0),exit_button, 2)    
            #

            pygame.display.update()
            
    #=============================================================================================================================================================#

    printer.goodbye(myname,version)
    
if __name__ == '__main__': zerogAlive()

def dephaser():
    ph=phase
    if ph==-1: return "PHASE_NONE"
    if ph==0: return "PHASE_SHOWER"
    if ph==1: return "PHASE_FADE1"
    if ph==2: return "PHASE_FLOAT"
    if ph==3: return "PHASE_FADE2"
    if ph==4: return "PHASE_WAIT"
    if ph==5: return "PHASE_PLO"
    if ph==6: return "PHASE_PHI"
    if ph==70: return "PHASE_UV"
    if ph==76: return "PHASE_UV+PHI"
    if ph==800: return "PHASE_H2O2"
    if ph==806: return "PHASE_H2O2+PHI"
    if ph==870: return "PHASE_H2O2+UV"
    if ph==876: return "PHASE_H2O2+UV+PHI"
    if ph==9000: return "PHASE_SHUTOFF"
    return "WEIRD->"+str(ph)