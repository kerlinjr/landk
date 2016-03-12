# -*- coding: utf-8 -*-
"""
Created on Wed Mar 09 11:24:27 2016

@author: jrkerlin

Make condensed ngram frequency dictionaries containing only keys used in the current study 
byteify by Mark Amery
"""
import json

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input
        
from collections import defaultdict
import re
import os
rootDir = os.path.normpath("C:\TCDTIMIT\Dictionaries")
corpusDir = "SubtlexUS"
studyDir = "TCDTIMIT"
types = ['Tri']
for t in types:
    regex = re.compile("[^a-zA-Z0-9 '-]")
    corpusDict = byteify(json.load(open(os.path.join(rootDir,corpusDir, t + ".txt"))))
    studyTokens = byteify(json.load(open(os.path.join(rootDir,studyDir, t + ".txt"))))
    
    studyDict = defaultdict(int)
    for tok in studyTokens:
        if t != 'Dict':           
            tokstr = str(tuple(tok))
        else:
            tokstr = tok
        if corpusDict.has_key(tokstr):
            studyDict[tokstr] = corpusDict[tokstr]
        else:
            studyDict[tokstr] = 0   

    json.dump(studyDict, open(os.path.join(rootDir,studyDir, t + corpusDir + '.txt'),'w'))      