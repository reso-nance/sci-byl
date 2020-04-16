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

import argparse, os
from xml_cleaner import to_raw_text

parser = argparse.ArgumentParser()
parser.add_argument("inputFile", help="input file in .txt format")
parser.add_argument("-x", "--strip-xml", help="remove markup and <tags>", action="store_true")
parser.add_argument("-s", "--special-chars", help="remove non-alphanumerical characters except punctuation marks", action="store_true")
parser.add_argument("-n", "--numbers", help="remove digits and numbers", action="store_true")
parser.add_argument("-w", "--word-count", help="remove lines containing less than X words", type=int)
parser.add_argument("--numbered-lines", help="remove lines beginning with a number")
parser.add_argument("--markup-lines", help="remove lines beginning with < symbol")
args = parser.parse_args()

punctuation=[".", ",", "?", "!", ";", " ", ":", "\n", "’", "-"]

if not os.path.exists(args.inputFile) :
    raise SystemError("unable to find file "+args.inputFile)
filenameWithoutExt, extension = os.path.splitext(os.path.basename(args.inputFile))
outputFilename = filenameWithoutExt+"_parsed.txt"
if extension.upper() != ".TXT" :
    raise SystemError("input file isn't in supported format (.txt)")

with open(args.inputFile, "rt") as inputFile :
    with open(outputFilename, "wt") as outputFile :
        for line in inputFile.readlines():
            if args.strip_xml : line = "".join(to_raw_text(line, keep_whitespace=True)[0])
            if args.special_chars : line = "".join([c for c in line if c.isalnum() or c in punctuation])
            if args.numbers : line = "".join([c for c in line if not c.isdigit()])
            if args.word_count and len(line.split(" ")) < args.word_count : continue
            if args.numbered_lines and line.replace(" ","")[0].isdigit() : continue
            if args.markup_lines and line.replace(" ","")[0] == "<" : continue
            outputFile.write(line)

print("successfully parsed",args.inputFile,"to", outputFilename,"with options :\n",args)
