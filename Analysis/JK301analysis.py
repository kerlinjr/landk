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

##Just the spell correction and word -level scoring
#sc = landkit.SentCompare(['hello worlddsfg go','soul train with him'],['hellot mold','sol tarin'],False)
#sc.SpellCorrect()
#sc.ScoreWords()
dataDir = r'C:\TCDTIMIT\dataOut\JK301'
folders = os.walk(dataDir).next()[1]
csvNames =[]
wavNames = []
lktable = pd.DataFrame()
for folder in folders:
     talkerDir = os.listdir(os.path.join(dataDir,folder))
     for folder2 in talkerDir:
         blockFolder = os.path.join(dataDir,folder, folder2)
         csvName = [os.path.join(blockFolder,f) for f in os.listdir(blockFolder) if fnmatch.fnmatch(f, '*.csv')]
         wavNames = [blockFolder + '\\' + f for f in os.listdir(blockFolder) if fnmatch.fnmatch(f, '*.wav')]
         lks= pd.read_csv(csvName[0])
         lks['VerbalResponse'] = wavNames
         lktable = lktable.append(lks)
         
lktable = lktable.reset_index()
# Set all non-responses to a single black         
lktable['SourceSentence'] = lktable['SourceSentence'].fillna(" ")        
sc = landkit.SentCompare(list(lktable['TargetSentence']),list(lktable['SourceSentence']),True)
filehandler = open(dataDir + '\\sc.pickle', 'w') 
pickle.dump(sc, filehandler)

sc.phonTable.to_csv(dataDir+'\\phonTable.csv')

# Make pandas table 
sentT = pd.DataFrame(lktable)

#Join the ngram and IPHoD info and "correctness"  at the word level
wordT = pd.concat([sc.tngram, sc.tphod], axis=1, join_axes=[sc.tngram.index])

#wordT['HitIndex']= [y for x in sc.hits for y in x]
#wordT['WordIndex']= [y for x in sc.hits for y,z in enumerate(x)]


#
#Table with phoneme Level info
phonT = sc.phonTable
bigPhonT = pd.concat([landkit.IndexFill(sentT,phonT['SentenceCount'],phonT['PhonemeCount']),landkit.IndexFill(wordT,phonT['WordCount'],phonT['PhonemeCount']),phonT], axis=1, join_axes=[phonT.index])


##Featurize all the phonemes
#phonSet = set(bigPhonT['TargetPhoneme'])
#for phon in phonSet:
#    bigPhonT['Phon_' +phon] = bigPhonT['TargetPhoneme'] == phon


bigPhonT.to_csv(dataDir+'\\bigP.csv')
bigSentT = bigPhonT.groupby('SentenceCount').first()

#Word Summaries
bigWordT = bigPhonT.groupby('WordCount').first()
bigWordTMean = bigPhonT.groupby('WordCount').mean()
bigWordT.iloc[:,-len(phonSet):] = bigWordTSum.iloc[:,-len(phonSet):] 

#First phoneme failure
lessCommon = missedPhon.loc[bigPhonT['1LogGram']<18]
missedPhon = lessCommon.loc[lessCommon['PhonemeHitBool'] == False]
firstMissedPhon = missedPhon.groupby('SentenceCount').first()
firstMissWords = firstMissedPhon.groupby('TargetWord').size()
firstMissPhons = firstMissedPhon.groupby('TargetPhoneme').size()
allPhons = lessCommon.groupby('TargetPhoneme').size()
firstMissPhons/float(firstMissPhons.sum())-allPhons/float(allPhons.sum())
firstMissPhons/float(firstMissPhons.sum())
firstMissWords.sort_values

firstMissWords.to_csv(dataDir+'\\firstMissWords.csv')

bigWordT.to_csv(dataDir+'\\bigW.csv')
bigSentT.to_csv(dataDir+'\\bigS.csv')
#del(sc) #clear memory

#from ATTEngine import ATTSpeech
#a = ATTSpeech()
#a.text_from_file(r'C:\TCDTIMIT\volunteersSmall\s01M\straightcam\sa1.wav')
#
#for snum,bools in enumerate(sc.hits_phonemes):
#   print sc.target_phonemes[snum]
#   print sc.source_phonemes[snum]
#   print bools
##
#sentenceACC = []
#for snum,bools in enumerate(sc.hits_phonemes):
#    print sc.target[snum]
#    print sc.source[snum]
#    booze = [int(boo) for boo in bools]
#    acc = sum(booze)/float(len(booze))
#    sentenceACC.append(acc)
##
#hitp = []
#missp = []
#for snum,bools in enumerate(sc.hits_phonemes):
#    phon,wordIdx,word =  zip(*sc.target_phonemes[snum])
#    for pnum,p in enumerate(phon):
#        if bools[pnum]:
#            hitp.append(p)
#        else:
#            missp.append(p)    
#
#full = hitp+missp
#fullset = set(full)
#hitd ={}
#missd ={}
#accd ={}
#for p in fullset:
#    hitd[p] = 0
#    missd[p] = 0
#for p in hitp:
#    hitd[p] = hitd[p]+1
#for p in missp:
#    missd[p] = missd[p]+1
#for p in fullset:
#    accd[p] = hitd[p]/float(hitd[p]+missd[p]) 
    
#figure(num=None, figsize=(16, 5), dpi=80, facecolor='w', edgecolor='k')
#bar(range(len(accd)), accd.values(), align='center')
#xticks(range(len(accd)), accd.keys())
#

