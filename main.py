#!/usr/bin/env python
#!/usr/bin/env python3
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

import os, signal, time, random, glob
from datetime import datetime, timedelta
import markov, leds, audio

debug = False
audioFolder = "./wav"
randomInterval = 30 # time in seconds where the probability to play a random wav is evaluated
randomThreeshold = .03 # probability of the wav being played in this interval (in percent)
loopDelay = 0.01 # in seconds
byeMessages=["je dois me reposer", "qui a éteint la lumière ?", "fais de beaux rêves toi aussi", "c'est pas trop tôt",
"j'ai hâte de te revoir", "je dors à poings fermés, et toi ?", "erreur système : j'ai pas sommeil"]

def exitCleanly(*args, shutdown=False):
    leds.GPIO.cleanup()
    if shutdown is True : os.system("sudo shutdown now")
    raise SystemExit
    
if __name__ == '__main__':
    signal.signal(signal.SIGTERM, exitCleanly) # register this exitCleanly function to be called on sigterm
    print("setting up GPIOs ...")
    leds.setup()
    leds.setRGB([0,0,100])
    print("initialising corpuses ...")
    markov.initialiseCorpuses()
    print("starting to breathe")
    leds.startBreathing()
    audioFiles = glob.glob(audioFolder+"/*.wav")
    audioFiles += glob.glob(audioFolder+"/*.WAV")
    print("audio files availables :", audioFiles)
    wasButtonPressed = leds.readButton()
    shutdownTimer = None
    randomWavTimer = datetime.now()+timedelta(seconds=randomInterval)
    try:
        while True : 
            if debug :
                selectedFile = audioFiles[random.randint(0, len(audioFiles)-1)]
                audio.play(selectedFile)
                print("playing random sample", selectedFile)
                time.sleep(10)
                markov.generateText(300)
                time.sleep(20)
            else :
                isButtonPressed = leds.readButton()
                if isButtonPressed :
                    if not wasButtonPressed : # the button is pressed for the first time
                        print("button is pushed")
                        shutdownTimer = datetime.now() + timedelta(seconds=5) #if maintained 5sec, it will shut the pi down
                        markov.generateText(300)
                    elif shutdownTimer and datetime.now() > shutdownTimer :
                        audio.isPlaying = False
                        markov.readTextToSpeech(random.choice(byeMessages))
                        time.sleep(5)
                        # exitCleanly(shutdown=True)
                elif shutdownTimer : shutdownTimer = False
                wasButtonPressed = isButtonPressed
                time.sleep(loopDelay)
                if datetime.now() > randomWavTimer :
                    if random.random() <= randomThreeshold :
                        selectedFile = random.choice(audioFiles)
                        if not audio.isPlaying : audio.play(selectedFile)
                        print("playing random sample", selectedFile)
                    randomWavTimer+=timedelta(seconds=randomInterval)
    except KeyboardInterrupt: exitCleanly() # quit on ^C
