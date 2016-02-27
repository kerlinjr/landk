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
reader = nltk.corpus.reader.PlaintextCorpusReader('C:\\TCDTIMIT\\' , 'Subtlex.US_UTF8.txt') #Original file ANSI encoded, doesn't work!
allWords = reader.words()
#JSON method
import json

#fdist = nltk.FreqDist(w.lower() for w in allWords)
#json.dump(fdist, open("C:\TCDTIMIT\SubtlexDict.txt",'w'))
#writer = csv.writer(open("C:\TCDTIMIT\SubtlexDict.txt", 'wb'))
#for key, value in fdist.items():
#    writer.writerow([key, value])
   
allBi = defaultdict(int)
for x,sent in  enumerate(reader.sents()):
    for bi in list(nltk.bigrams(sent)):
        allBi[bi] += 1
    if x % 10000 == 0:
            print "Sentence Bi"+ str(x)
            
json.dump(allBi, open("C:\TCDTIMIT\SubtlexBi.txt",'w'))
            
#writer = csv.writer(open("C:\TCDTIMIT\SubtlexBi.txt", 'wb'))
#for key, value in allBi.items():
#   writer.writerow([key, value])
#   
allTri = defaultdict(int)
for x,sent in  enumerate(reader.sents()):
    for tri in list(nltk.trigrams(sent)):
        allTri[tri] += 1
        if x % 10000 == 0:
            print "Sentence Tri"+ str(x)   

json.dump(allTri, open("C:\TCDTIMIT\SubtlexTri.txt",'w'))
#            
#writer = csv.writer(open("C:\TCDTIMIT\SubtlexTri.txt", 'wb'))
#for key, value in allTri.items():
#   writer.writerow([key, value])
#      
#   
#reader = csv.reader(open("C:\TCDTIMIT\SubtlexDict.txt", 'rb'))
#mydict = dict(reader)



mydict = json.load(open("C:\TCDTIMIT\SubtlexDict.txt"))
