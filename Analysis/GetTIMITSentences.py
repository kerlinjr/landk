# -*- coding: utf-8 -*-
"""
Created on Tue Mar 08 10:46:59 2016

@author: jrkerlin

Gets the all the TIMIT sentences

"""
import os
import fnmatch
import nltk 
import json
import re
import inflect
inflectEngine = inflect.engine() 

allSents = [] 
allWords = []
allBi = []
allTri = []
talkerPath = r'C:\TCDTIMIT\volunteersSmall'
regex = re.compile("[^a-zA-Z0-9 '-]")
folders = os.listdir(talkerPath)
for folder in folders:    
    path = os.path.join(talkerPath,folder,'straightcam')
    files = [p for p in os.listdir(path) if fnmatch.fnmatch(p,'*.txt')]
    for fname in files:
        sent = []
        f = open(os.path.join(path,fname))
        for line in f:
            line = regex.sub('',line)
            linesplit = line.split(" ")[2].strip('\n').encode('utf8')
            for x,w in enumerate(linesplit):
                if w.isdigit():
                    linesplit[x] = inflectEngine.number_to_words(w)
            sent.append(linesplit)
        allSents.append(sent)
        allWords.extend(sent)
        allBi.extend(list(nltk.bigrams(sent)))
        allTri.extend(list(nltk.trigrams(sent)))

json.dump(allSents, open("C:\TCDTIMIT\Dictionaries\TCDTIMIT\Sents.txt",'w'))
json.dump(allWords, open("C:\TCDTIMIT\Dictionaries\TCDTIMIT\Dict.txt",'w'))  
json.dump(allBi, open("C:\TCDTIMIT\Dictionaries\TCDTIMIT\Bi.txt",'w'))  
json.dump(allTri, open("C:\TCDTIMIT\Dictionaries\TCDTIMIT\Tri.txt",'w'))





           
        
        