#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
#  Copyright 2020 Reso-nance Numérique <laurent@reso-nance.org>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#      -------------- Pinout --------------
#            RPI
#      pin 12 (GPIO18) ------> IRLZ34N gate
#      pin 19 (GPIO10) ------> MCP3008 MISO
#      pin 21 (GPIO09) ------> MCP3008 MOSI
#      pin 23 (GPIO11) ------> MCP3008 CLK
#      pin 24 (GPIO08) ------> MCP3008 CS
#  

import RPi.GPIO as GPIO
import math, random, time
from threading import Thread
from datetime import datetime, timedelta

RGBpinsNumber = [11, 13, 15] # BOARD numbers
buttonPin = 10
ledRefresh = 5 # delay in ms between two LED updates
RGBPins = []
isBreathing = False
isLit = False

def setup():
    """ setup GPIO PWM pins output and button input"""
    global RGBPins
    GPIO.setmode(GPIO.BOARD)
    for pin in RGBpinsNumber :
        GPIO.setup(pin, GPIO.OUT)
        RGBPins.append(GPIO.PWM(pin, 120)) # tried 50hz but some flickering was clearly visible
        RGBPins[-1].start(0)
    # GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(buttonPin, GPIO.IN) # no need for pullups/downs since the capacitive module has them on board

def breathe(intensityFreq, colorFreq, pause):
    """will make the RGB led change color and intensity according to the frequencies given (in Hz) until isBreathing is set to False"""
    global isLit, isBreathing, RGBPins
    if isLit : isLit = False
    if not isBreathing : isBreathing = True
    timeStarted = datetime.now()
    intensityFreq, colorFreq = 2.0*math.pi*intensityFreq, 2.0*math.pi*colorFreq # convert freq from Hz to rad
    while isBreathing :
        sleepTime = timedelta(milliseconds=ledRefresh)
        while timeStarted+sleepTime > datetime.now(): pass # way more accurate than time.sleep()
        intensityValue = getSineValue(timeStarted, intensityFreq)
        colorValue = getSineValue(timeStarted, colorFreq)
        if pause and intensityValue < 0.02: 
            timeStarted += timedelta(seconds=pause-.01) # we are making a pause when the intensity is very low
            print("pause")
            time.sleep(pause)
        RGBvalues = hsv2rgb(colorValue, 1., intensityValue) # translate HSV into RGB
        for i in range(3) : RGBPins[i].ChangeDutyCycle(RGBvalues[i]) # write to LEDs

def startBreathing(intensityFreq=.3, colorFreq=.05, pause=None) :
    """will make the RGB led change color and intensity according to the frequencies given (in Hz) until isBreathing is set to False"""
    Thread(target=breathe, args=(intensityFreq, colorFreq, pause)).start()

def getSineValue(timeStarted, frequency):
    """ returns a value between 0 and 1 corresponding to a sinewave at a given frequency"""
    # frequency = 2.0*math.pi*frequency # convert freq from Hz to radians
    timeElapsed = (datetime.now()-timeStarted).total_seconds()
    return (1.0 + math.sin(timeElapsed*frequency))/2.0

def hsv2rgb(h, s, v):
    """returns 0-100 rgb values from 0-1 hsv, shamelessly copy/pasted from stackoverflow"""
    if s == 0.0: v*=100; return (v, v, v)
    i = int(h*6.)
    f = (h*6.)-i; p,q,t = int(100*(v*(1.-s))), int(100*(v*(1.-s*f))), int(100*(v*(1.-s*(1.-f)))); v*=100; i%=6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)   

def readButton(): 
    """will return True if the buttonPin is HIGH or False otherwise"""
    return GPIO.input(buttonPin) == GPIO.HIGH

def setRGBthread(RGBvalues) :
    """lights RGB led to fixed values until isLit is set to False"""
    global isBreathing, isLit, RGBPins
    if isBreathing : isBreathing = False
    if not isLit : isLit = True
    for i in range(3) : # begin PWM on RGB pins
        RGBPins[i].ChangeDutyCycle(RGBvalues[i])
    while isLit : time.sleep(.05)
    for i in range(3) : RGBPins[i].ChangeDutyCycle(0)

def setRGB(RGBvalues):
    """lights RGB led to fixed values until isLit is set to False"""
    Thread(target=setRGBthread, args=(RGBvalues,)).start()

def setHSV(hue, saturation, value): 
    """lights RGB led to fixed hue, saturation and value (0-1) until isLit is set to False"""
    global RGBPins
    RGBvalues = hsv2rgb(hue, saturation, value)
    for i in range(3): RGBPins[i].ChangeDutyCycle(RGBvalues[i])

if __name__ == '__main__':
    print("this file is made to be imported as a module, not executed")
    raise SystemError
