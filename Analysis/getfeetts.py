# -*- coding: utf-8 -*-
"""
Created on Tue Feb 02 11:26:58 2016

@author: Stephen Marquard 
"""

import sys

root = "/data/src/sphinx/tools/freetts-1.2.2"
libDir = root + "/lib/"

ltsRules = root + "/bld/classes/com/sun/speech/freetts/en/us/cmulex_lts.bin"

classPaths = [
    "freetts.jar",
    "cmulex.jar"
]

for classPath in classPaths:
    sys.path.append(libDir + classPath)

true = 1
false = 0

from com.sun.speech.freetts.lexicon import LetterToSound
from com.sun.speech.freetts.lexicon import LetterToSoundImpl

from java.net import URL

lts = LetterToSoundImpl(URL("file:" + ltsRules), true);

lines = sys.stdin.readlines()

for line in lines:

    word = line.strip()

    if (word != "") :

        phones = lts.getPhones(word, None)

        print word.upper() + "\t",

        for phone in phones:

            # Remove stress marks
            if (phone.endswith("1") or phone.endswith("2")):
                phone = phone.strip("12");

            # Replace AX with AH for compatibility with CMU Sphinx 40 phoneset
            if (phone == "ax"):
                phone = "ah"

            print phone.upper(),

        print