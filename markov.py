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

import markovify, os, sys, re, spacy, glob, json, random, subprocess
from threading import Thread
import audio

scriptPath = os.path.abspath(os.path.dirname(__file__))
corpusPath = scriptPath+"/corpus/"
availableCorpuses = None
textToSpeech = True

# overriding POSifiedText to make use of spacy
nlp = spacy.load("fr_core_news_sm")
class POSifiedText(markovify.Text):
    def word_split(self, sentence):
        return ["::".join((word.orth_, word.pos_)) for word in nlp(sentence)]

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence

if __name__ == '__main__':
    raise SystemExit("This file is not meant to be executed directly. It should be imported as a module.")
    
def generateText(sentenceLength = 280):
    """will output a sentence generated from a random model"""
    model = random.choice(availableCorpuses)
    print("selected model :", model["name"])
    for i in range(10):
        text = model["model"].make_short_sentence(sentenceLength)
        if text is not None : 
            if textToSpeech : readTextToSpeech(text)
            print(text)
            return
        else : sentenceLength -= 20 # shorter sentences are easier to generate
    print("unable to generate text 10 times in a row")

def epub2txt(path, extension):
    """ converts an epub to a .txt file using ebooklib, returns the new .txt path"""
    outputPath = path.replace(extension, ".txt")
    from epub_conversion.utils import open_book, convert_epub_to_lines
    from xml_cleaner import to_raw_text
    lines = convert_epub_to_lines(open_book(path))
    for line in lines :
        line = to_raw_text(line)[0] # we strip out markup
        if len(line) > 15 and line[0] != "<" : # we only keep longer lines to avoid titles and pagination
            line = " ".join(line) + "\n"
            with open(outputPath, "a") as f : f.write(line)
    return outputPath

def buildModel(filename):
    """ constructs a precomputed .json model from a text file"""
    if not os.path.isfile(filename) :
        print("file %s not found" % filename)
        return False
    corpus = open(filename).read()
    textModel = markovify.Text(corpus, state_size=3)
    JSONmodel = textModel.to_json()
    with open (os.path.splitext(filename)[0]+".json", "w", encoding="utf-8") as f :
        json.dump(json.loads(JSONmodel), f, ensure_ascii=False, indent=4)
        return True

def loadModelFromJson(path):
    with open(path, "r", encoding="utf-8") as json_file:
        data = json.dumps(json.load(json_file))
    model = markovify.Text.from_json(data)
    return {"model":model, "length":len(data)}

def initialiseCorpuses():
    """will search available text files, look for a corresponding json precomputed model and generate one if missing"""
    global availableCorpuses
    availableCorpuses = []
    for path in glob.glob(corpusPath+"*.txt")+glob.glob(corpusPath+"*.epub") :
        pathWithoutExt = os.path.splitext(path)[0]
        filename, extension, filenameWithoutExt = os.path.basename(path), os.path.splitext(os.path.basename(path))[1], os.path.splitext(os.path.basename(path))[0]
        if not os.path.isfile(pathWithoutExt+".json") :
            print("  new corpus %s found, computing model..." % filename)
            if extension.upper() == ".EPUB" and not os.path.isfile(pathWithoutExt+".txt"):
                path = epub2txt(path, extension) # convert the .epub to .txt if it ain't already done
            if not buildModel(path) :
                print("ERROR computing %s model" % filename)
                break
        else : print("  using precomputed corpus %s" % filenameWithoutExt)
        model = loadModelFromJson(pathWithoutExt+".json")
        availableCorpuses.append({"name":filenameWithoutExt,"model":model["model"],"length":model["length"], "mix":.5})
    print("\n---corpuses initialised successfully---\n")
    return

def readTextToSpeech(text):
    """uses pico2wav to produce a 16kHz wav which is converted to 44.1kHz by sox then played using audio.play()"""
    cmd = 'pico2wave --lang="fr-FR" -w tmp16kHz.wav "'+text+'" && sox tmp16kHz.wav -r 44100 tmp.wav' #pico2wave only generate 16kHz wavs which cannot be read by pyaudio
    subprocess.Popen(cmd, shell=True).wait()
    audio.play("./tmp.wav")