# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 09:12:55 2016

@author: jrkerlin
"""

"""Makes ngram frequency dictionary's out of the SubtlexUS corpus 

"""
import nltk
#import csv
from collections import defaultdict
reader = nltk.corpus.reader.PlaintextCorpusReader('C:\\TCDTIMIT\\Dictionaries\\SubtlexUS\\' , 'Subtlex.US_UTF8.txt',nltk.WhitespaceTokenizer()) #Original file ANSI encoded, doesn't work!
#JSON method
import json
import re
import inflect 
inflectEngine = inflect.engine()

switch = 'tri'

regex = re.compile("[^a-zA-Z0-9 '-]")
if switch == 'uni':
    allDict = defaultdict(int)
    for x,sent in enumerate(reader.sents()):
        esent = regex.sub('', " ".join(sent).encode('utf8').lower().strip(" ")).replace("  "," ").strip(" ").split(" ")   
        for y,w in enumerate(esent):
                if w.isdigit():
                    esent[y] = inflectEngine.number_to_words(w)        
        for uni in esent:        
            allDict[str(uni)] += 1
        if x % 10000 == 0:
            print "Sentence Dict"+ str(x)
            print "Dictionary length: " +str(len(allDict))
    json.dump(allDict, open("C:\TCDTIMIT\Dictionaries\SubtlexUS\Dict.txt",'w'))
    #writer = csv.writer(open("C:\TCDTIMIT\SubtlexDict.txt", 'wb'))
    #for key, value in fdist.items():
    #    writer.writerow([key, value])
elif switch == 'bi':    
    allBi = defaultdict(int)
    for x,sent in  enumerate(reader.sents()):
        esent = regex.sub('', " ".join(sent).encode('utf8').lower().strip(" ")).replace("  "," ").strip(" ").split(" ")    
        for y,w in enumerate(esent):
            if w.isdigit():
                esent[y] = inflectEngine.number_to_words(w)          
        for bi in list(nltk.bigrams(esent)):
            allBi[str(bi)] += 1
        if x % 10000 == 0:
                print "Sentence Bi"+ str(x)
                print "Dictionary length: " +str(len(allBi))
                
    json.dump(allBi, open("C:\TCDTIMIT\Dictionaries\SubtlexUS\Bi.txt",'w'))
            
#writer = csv.writer(open("C:\TCDTIMIT\SubtlexBi.txt", 'wb'))
#for key, value in allBi.items():
#   writer.writerow([key, value])
#   
elif switch == 'tri':            
    allTri = defaultdict(int)
    for x,sent in  enumerate(reader.sents()):
        esent = regex.sub('', " ".join(sent).encode('utf8').lower().strip(" ")).replace("  "," ").strip(" ").split(" ")    
        for y,w in enumerate(esent):
            if w.isdigit():
                esent[y] = inflectEngine.number_to_words(w)        
        for tri in list(nltk.trigrams(esent)):
            allTri[str(tri)] += 1
        if x % 10000 == 0:
                print "Sentence Tri"+ str(x)
                print "Dictionary length: " +str(len(allTri))
    
    json.dump(allTri, open("C:\TCDTIMIT\Dictionaries\SubtlexUS\Tri.txt",'w'))
#            
#writer = csv.writer(open("C:\TCDTIMIT\SubtlexTri.txt", 'wb'))
#for key, value in allTri.items():
#   writer.writerow([key, value])
#      
#   
#reader = csv.reader(open("C:\TCDTIMIT\SubtlexDict.txt", 'rb'))
#mydict = dict(reader)

#mydict = json.load(open("C:\TCDTIMIT\SubtlexDict.txt"))
