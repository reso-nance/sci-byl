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

import time, os, pyaudio, numpy, wave, random
from threading import Thread
import leds
isPlaying = False


chunkSize = 4096

def playThread(filename) :
    global isPlaying
    isPlaying = True
    wavfile = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()
    print("playing file", filename, " : format",p.get_format_from_width(wavfile.getsampwidth()), "rate",  wavfile.getframerate())
    stream = p.open(format = p.get_format_from_width(wavfile.getsampwidth()),
                    channels = wavfile.getnchannels(),
                    rate = wavfile.getframerate(),
                    output = True)
    data = wavfile.readframes(chunkSize)
    color = random.random() # this color will be used to animate the lights
    leds.isBreathing = False # stop the breathing
    # Play the sound by writing the audio data to the stream
    while data and isPlaying:
        stream.write(data)
        numpydata = numpy.frombuffer(data[::2], dtype=numpy.int16) # we use numpy on half the list to process the mean quicker
        mean = min(1, numpy.mean(numpy.absolute(numpydata)) /10000) # this value will give us an estimate of the loudness 0-1
        leds.setHSV(color, 1, mean) # we dim the lights
        data = wavfile.readframes(chunkSize)

    # Close and terminate the stream
    stream.close()
    p.terminate()
    isPlaying = False
    leds.startBreathing()

def play(filename):
    Thread(target=playThread, args=(filename,)).start()


if __name__ == '__main__':
    print("this file is made to be imported as a module, not executed")
    raise SystemError
