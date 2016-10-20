# -*- coding: utf-8 -*-
"""
Created on Tue Mar 08 10:46:59 2016

@author: jrkerlin

Gets the all the TIMIT sentences

"""
import os
import fnmatch
import re
import pandas as pd
import numpy as np
from collections import defaultdict 
import random

talkerLabel = []
sentenceType = []
fullpath  = []
fileName = []
gender = []
numWords =[]
cnt = 0
talkerPath = r'C:\TCDTIMIT\volunteersSmall'
regex = re.compile("[^a-zA-Z0-9 '-]")
folders = os.listdir(talkerPath)[:-1] # Don't include the test subject
for talker in folders:    
    path = os.path.join(talkerPath,talker,'straightcam')
    files = [p for p in os.listdir(path) if fnmatch.fnmatch(p,'*.mp4')]
    for fname in files:
        f = open(os.path.join(path,fname[:-4]+'.txt'))
        wordCnt = 0
        for line in f:
            wordCnt+=1
        talkerLabel.append(talker)
        sentenceType.append(fname[0:2])
        fileName.append(fname[:-4])
        gender.append(talker[3])
        numWords.append(wordCnt)
      
df = pd.DataFrame(np.transpose([talkerLabel, sentenceType, fileName, gender, numWords]), columns =['Talker','SentenceType','SentenceID','Gender','NumWords'])
talkerExclude = ['s06M','s22M','s27M','s42M','s21M',] # Under 80% clear performance, > 2 std performance for an individual, timing test 
maxNumWords = 10
df = df[~df['Talker'].isin(talkerExclude)]
df = df[df['NumWords'].astype(int) <= 10]
df = df[df['SentenceType'].isin(['sx','si'])]





desiredTrialsPerTalker = 20
d = defaultdict(int)
attempt = 0

while sum(pd.DataFrame.from_dict(d,orient ='index').values) != desiredTrialsPerTalker*54:
    bannedTalkers =[]
    dfTmp = df
    d = defaultdict(int)
    trlIdx = []
    sentids = np.unique(dfTmp['SentenceID'].values)
    np.random.shuffle(sentids)
    for sentid in sentids:
        boolSent = dfTmp['SentenceID'].isin([sentid]) & ~dfTmp['Talker'].isin(bannedTalkers)
        tab = np.array(dfTmp.loc[boolSent].index)
        if tab.size > 0:
            trlIdx.append(np.random.choice(tab,1)[0]) #Select random qualifying trial
            talk= [dfTmp.loc[trlIdx[-1]].Talker][0]
            d[talk]+=1
            if d[talk] == desiredTrialsPerTalker:
                bannedTalkers.append(talk)# Remove talkers with 8 sx sentences from consideration          
    attempt+=1
    print attempt
    
dfPick = df[df.index.isin(trlIdx)]
dfPick = dfPick.sort_values('Talker')

design = [0,0,0,0,0,1,1,1,1,1,2,2,2,2,2,3,3,3,3,3]
numreps = 4
repetition = np.kron(np.arange(0,4), np.ones(len(dfPick)))
avOrder = []

for rep in np.arange(0,4):
    for talker in np.unique(dfPick['Talker']):
        avOrder.extend(np.random.choice(design,desiredTrialsPerTalker,replace = False))

#avOrder = np.hstack([avOrder1,avOrder2,avOrder3,avOrder4])
    
soundLabels = ['Babble','Babble','Babble','Babble']
videoLabels = ['AO','AO','AO','AO']
targetLabels = ['Present','Present','Present','Absent']
#ProbeLabels = ['Before','After','Before','After']

dfPickFull = pd.concat([dfPick,dfPick,dfPick,dfPick])   
dfPickFull['AVOrder'] = avOrder
dfPickFull['SoundCond'] = [soundLabels[x] for x in avOrder]
dfPickFull['VideoCond'] = [videoLabels[x] for x in avOrder]
dfPickFull['TargetCond'] = [targetLabels[x] for x in avOrder]
dfPickFull['Repetition'] = repetition

#Randomize the talker order and trial order for each condition counterbalanced set
totalTrlOrder =[]
trlOrder = []
babbleOrder= []
randTalkerOrder = np.arange(0,len(np.unique(dfPick['Talker'])))
blockTrlOrder = np.arange(0,desiredTrialsPerTalker)
bOrder = np.arange(0,desiredTrialsPerTalker)
for y in np.arange(0,4):
    np.random.shuffle(randTalkerOrder)
    for x in randTalkerOrder:
        np.random.shuffle(blockTrlOrder)
        np.random.shuffle(bOrder)
        trlOrder.extend(blockTrlOrder+1)
        babbleOrder.extend(bOrder+1)
        totalTrlOrder.extend(blockTrlOrder+x*desiredTrialsPerTalker+y*len(dfPick)+1)
dfPickFull['TrialOrder'] = trlOrder
dfPickFull['BabbleFile'] = babbleOrder
dfPickFull['TotalTrialOrder'] = totalTrlOrder
dfPickFull = dfPickFull.set_index('TotalTrialOrder').sort_index()
#Put all the subjects in order 
numSubs = 12
subNum=[]
subTalkerNum =[]
probeBeforeAfter = []
probeDelay = []
for x in np.arange(1,numSubs+1):
    subNum.extend(np.ones(len(dfPickFull)/numSubs)*(x))
    subTalkerNum.extend(np.kron(np.arange(1,19),np.ones(desiredTrialsPerTalker)))
#    if x % 2 == 1:
    probeDelay.extend(np.kron(np.array([2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]),np.ones(desiredTrialsPerTalker)))
#    else:
#        probeDelay.extend(np.kron(np.array([2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1]),np.ones(desiredTrialsPerTalker)))
    if x % 2 == 1:
        probeBeforeAfter.extend(np.kron(np.array([2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1]),np.ones(desiredTrialsPerTalker)))
    else:
        probeBeforeAfter.extend(np.kron(np.array([1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]),np.ones(desiredTrialsPerTalker)))
            
probePosition = []        
for x in np.arange(1,len(dfPickFull)+1):
    if dfPickFull['TargetCond'][x] == 'Present':
        probePosition.append(np.random.randint(int(dfPickFull['NumWords'][x])))
    else:
        probePosition.append(-1)
       
dfPickFull['Subject'] = subNum
dfPickFull['SubjectTalkerNum'] = subTalkerNum
dfPickFull['ProbePosition'] = probePosition
dfPickFull['ProbeBeforeAfter'] = probeBeforeAfter
dfPickFull['ProbeBeforeAfter'] = dfPickFull['ProbeBeforeAfter'].apply(lambda x: 'Before' if x == 1 else 'After')
dfPickFull['ProbeDelay'] = probeDelay
dfPickFull['ProbeDelay'] = dfPickFull['ProbeDelay'].apply(lambda x: 'Delay' if x == 1 else 'No Delay')


dfPickFull.to_csv('C:\Experiments\JK311\StudyDesignJK311.csv')