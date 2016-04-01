# -*- coding: utf-8 -*-
"""
Analysis script 

Created on Thu Jan 21 15:48:07 2016

@author: jrkerlin
"""
import os
import fnmatch
import pandas as pd
import numpy as np
import pickle
from matplotlib import *
import sys

#Add path to landkit

sys.path.append(r'C:\Users\jrkerlin\Documents\GitHub\landk\Analysis')
import landkit
reload(landkit)

def normjoin(*arg):
    return os.path.normpath(os.path.join(*arg))

##Just the spell correction and word -level scoring
#sc = landkit.SentCompare(['hello worlddsfg go','soul train with him'],['hellot mold','sol tarin'],False)
#sc.SpellCorrect()
#sc.ScoreWords()
dataDir = normjoin('C:\Experiments\JK302\dataOut')
folders = os.walk(dataDir).next()[1]
csvNames =[]
wavNames = []
lktable = pd.DataFrame()
for subjectDir in folders:
     blockFolder = normjoin(dataDir,subjectDir)
     csvNames = [normjoin(blockFolder,f) for f in os.listdir(blockFolder) if fnmatch.fnmatch(f, '*.csv')]
     for section in csvNames:
         lks= pd.read_csv(section)
         lktable = lktable.append(lks)
         print "Now Loading Subject..."+" ".join([subjectDir])
lktable = lktable.reset_index()

# Set all non-responses to a single black         
lktable['SourceSentence'] = lktable['SourceSentence'].fillna(" ")        
sc = landkit.SentCompare(list(lktable['TargetSentence']),list(lktable['SourceSentence']),True,normjoin('C:\Experiments\JK302'))
filehandler = open(dataDir + '\\sc.pickle', 'w') 
pickle.dump(sc, filehandler)

sc.phonTable.to_csv(dataDir+'\\phonTable.csv')

# Make pandas table 
sentT = pd.DataFrame(lktable)

#Join the ngram and IPHoD info and "correctness"  at the word level
wordT = pd.concat([sc.tngram, sc.tphod], axis=1, join_axes=[sc.tngram.index])
#
#Table with phoneme Level info
phonT = sc.phonTable
bigPhonT = pd.concat([landkit.IndexFill(sentT,phonT['SentenceCount'],phonT['PhonemeCount']),landkit.IndexFill(wordT,phonT['WordCount'],phonT['PhonemeCount']),phonT], axis=1, join_axes=[phonT.index])
bigPhonT.to_csv(dataDir+'\\bigP.csv')


