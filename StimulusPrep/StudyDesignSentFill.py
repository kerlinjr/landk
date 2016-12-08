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
df = df[df['NumWords'].astype(int) >= 4]
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
                bannedTalkers.append(talk)# Remove talkers with 20 si-sx sentences from consideration          
    attempt+=1
    print attempt
    
dfPick = df[df.index.isin(trlIdx)]
dfPick = dfPick.iloc[np.random.permutation(len(dfPick))].reset_index()
audioTable = pd.DataFrame.from_csv(r'C:\TCDTIMIT\Tables\audioTableTM.csv')
margin = 300 # Time in ms from sentence onset to possible noise insert
sampMargin = margin/float(1000)*48000
noisePhons = ['Y','B','W','P','M','K','D','N'] #ordered from least to most frequent in the TIMIT corpus
phonGroup =  ['Low','High','High','High','High','Low','Low','Low']
numPerGender = 48
dfPickF = dfPick[dfPick['Gender'] == 'F'].reset_index()
dfPickM = dfPick[dfPick['Gender'] == 'M'].reset_index()
#noisePicks = [x for x in range(0,numPerGender,1) if np.mod(x,4) in [0,1]]
for g in ['F','M']:
    phonUsed = [0, 0, 0, 0, 0, 0, 0, 0]
    if g == 'F':
        dfPickG = dfPickF
    else: 
        dfPickG = dfPickM
    dfPickG.ix[:,'PhonToNoise'] = 'None'  
    dfPickG.ix[:,'PTMIndex'] = -1  
    dfPickG.ix[:,'OnSampNoise'] = -1
    dfPickG.ix[:,'OffSampleNoise'] = -1
    dfPickG.ix[:,'SpeechOnset'] = -1
    dfPickG.ix[:,'SpeechOffset'] = -1
    dfPickG.ix[:,'SentDuration'] = -1
    for sentNum in dfPickG.index:
        print 'Now finding noise phoneme for sentence #' + str(sentNum)
        sentAtt = pd.merge(dfPickG.iloc[sentNum,:].to_frame().transpose(),audioTable,how = 'left', on = ['Talker','SentenceID'],suffixes =('','_y'))
        onSamp = int(sentAtt.OnsetSample[0])
        offSamp = int(sentAtt.OffsetSample[-1:])
        onSampMiss =np.abs(onSamp-48000)
        sentDur =int((sentAtt.OffsetSample[-1:]-sentAtt.OnsetSample[0]))/float(48000)
        margin1 = sentAtt.OnsetSample[0]+sampMargin
        margin2 = int(sentAtt.OffsetSample[-1:]-sampMargin)
        midSent = sentAtt.loc[(sentAtt.OnsetSample >= margin1) & (sentAtt.OnsetSample <= margin2) ]
        for num,nPhon in enumerate(noisePhons):

            if phonUsed[num] < numPerGender: # Only consider target phonemes that are not already filled
                if np.any(midSent.TargetPhoneme == nPhon): #only consider sentences with at least 1 of the target phonemes
                    if onSampMiss/float(48000) < .1: # remove sentences onsetting more than 100ms off 1 second
                        if sentDur < 4: # remove sentences longer than 4 seconds
                            print 'Found!'
                            phonUsed[num]+=1
                            samp = midSent.loc[midSent.TargetPhoneme == nPhon].sample(axis=0)
                            dfPickG.ix[sentNum,'PhonToNoise'] = nPhon
                            dfPickG.ix[sentNum,'PTMIndex'] = int(samp.PhonemeIndex)
                            dfPickG.ix[sentNum,'OnSampleNoise'] = int(samp.OnsetSample)
                            dfPickG.ix[sentNum,'OffSampleNoise'] = int(samp.OffsetSample)
                            dfPickG.ix[sentNum,'SpeechOnset'] = int(sentAtt.OnsetSample[0])
                            dfPickG.ix[sentNum,'SpeechOffset'] = int(sentAtt.OffsetSample[-1:])
                            dfPickG.ix[sentNum,'SentDuration'] = int((sentAtt.OffsetSample[-1:]-sentAtt.OnsetSample[0]))/float(48000)
                            dfPickG.ix[sentNum,'PhonRep'] = phonUsed[num]
                            dfPickG.ix[sentNum,'PhonVB'] = phonGroup[num]
#                            if np.mod(phonUsed[num],2):
#                                dfPickG.ix[sentNum,'AttendCond'] = 'AttendF'
#                            else:
#                                dfPickG.ix[sentNum,'AttendCond'] = 'AttendM'                        
#
#                            if phonUsed in noisePicks:
#                                dfPickG.ix[sentNum,'VideoCond'] = 'Audiovisual' 
#                            else
#                                dfPickG.ix[sentNum,'VideoCond'] = 'Auditory Only'
                            break
                                
        if np.all(np.array(phonUsed) == numPerGender):
            break            
    if g == 'F':
        dfPickF = dfPickG[dfPickG['PhonToNoise'] != 'None']
    else: 
        dfPickM = dfPickG[dfPickG['PhonToNoise'] != 'None']     
if len(dfPickM)+len(dfPickF) != numPerGender*len(noisePhons)*2:
    print 'Darn! Failed to find enough sentences'
else:
    print 'Super! Found enough sentences for this design!'     

dfFsort = dfPickF.groupby('PhonVB').apply(lambda x: x.sort_values('SentDuration')).drop(['level_0','PhonVB'],1).reset_index()
dfMsort = dfPickM.groupby('PhonVB').apply(lambda x: x.sort_values('SentDuration')).drop(['level_0','PhonVB'],1).reset_index()    
print np.mean(dfMsort['SentDuration'])
print np.std(dfFsort['SentDuration']-dfMsort['SentDuration'])
print max(np.abs(dfFsort['SentDuration']-dfMsort['SentDuration']))
print max(np.abs(dfFsort['SpeechOnset']-dfMsort['SpeechOnset']))
print max(np.abs(dfFsort['SpeechOffset']-dfMsort['SpeechOffset']))
if min(dfFsort['SpeechOffset']-dfMsort['OnSampleNoise']) < 0 or min(dfMsort['SpeechOffset']-dfFsort['OnSampleNoise']) < 0:
    print 'Fail! Noise onset may not overlap with opposite sentence!'

    

#Duplicate the trial sequence for each gender to attend

dfFsort =  dfFsort.reset_index().rename(columns ={'level_0': 'SpeechFileIndex'})
del dfFsort['index']
del dfFsort['level_1']
dfMsort =  dfMsort.reset_index().rename(columns ={'level_0': 'SpeechFileIndex'})
del dfMsort['index']
del dfMsort['level_1']
dfFsort.to_csv('C:\Experiments\SentFill\dfFsort.csv')
dfMsort.to_csv('C:\Experiments\SentFill\dfMsort.csv')

#Setup the CondKey
condKey = range(0,4)

noiseCond = ['F','F','M','M']
videoCond = ['Audiovisual','Auditory Only','Audiovisual','Auditory Only'] 
dfCond = pd.DataFrame([condKey,  noiseCond, videoCond]).transpose()
dfCond.columns = {'CondKey','NoiseCond','VideoCond'}
dfCond.to_csv('C:\Experiments\SentFill\dfCond.csv')

numSubs = 32
for subj in np.arange(1,numSubs+1):
    #Randomize the noise and video conditions within each VB value and Attended Gender
    dfSubOrder = pd.DataFrame()
    numTrialsPerGender = len(dfFsort)
    
    #Split Attended Gender into 2 blocks
    if np.mod(subj-1,4) in([0, 1]):
        dfSubOrder['AttendGender'] = np.concatenate([['F']*(numTrialsPerGender),['M']*(numTrialsPerGender)],axis = 0)
    elif np.mod(subj-1,4) in([2, 3]):    
        dfSubOrder['AttendGender'] = np.concatenate([['M']*(numTrialsPerGender),['F']*(numTrialsPerGender)],axis = 0)

    #Split Gender Location
    if np.mod(subj,2) in([1]):
        dfSubOrder['GenderLeft'] = ['F']*(numTrialsPerGender*2)
    elif np.mod(subj,2) in([0]):    
        dfSubOrder['GenderLeft'] = ['M']*(numTrialsPerGender*2)
    
    responsesPerGender = (numTrialsPerGender*1/float(8)/2) #Require response for 1 of 8 trials
    nonrespPerGender = numTrialsPerGender/2-responsesPerGender

    cKey = []
    respKey = []
    for x in np.arange(0,responsesPerGender/float(len(condKey))):
        cKey.extend(condKey)
        respKey.extend(np.ones(len(condKey))) 
    
    for x in np.arange(0,nonrespPerGender/float(len(condKey))):
        cKey.extend(condKey)
        respKey.extend(np.zeros(len(condKey))) 
        
    rp1 = np.random.permutation(np.arange(0,numTrialsPerGender/2)) 
    rp2 = np.random.permutation(np.arange(0,numTrialsPerGender/2))
    oneGenderCond1 = np.array(cKey)[rp1]
    oneGenderResp1 = np.array(respKey)[rp1]
    oneGenderCond2 = np.array(cKey)[rp2]
    oneGenderResp2 = np.array(respKey)[rp2]
    oneGenderConds = np.concatenate([oneGenderCond1,oneGenderCond2],axis = 0)
    oneGenderResps = np.concatenate([oneGenderResp1,oneGenderResp2],axis = 0)
    longConds = np.concatenate([oneGenderConds,oneGenderConds],axis = 0)
    longResps = np.concatenate([oneGenderResps,oneGenderResps],axis = 0)
    dfSubOrder['CondKey']= longConds
    dfSubOrder['RespKey']= longResps
    rp1 = np.random.permutation(len(dfSubOrder)/2)
    dfSubOrder['SpeechFileIndex'] = np.concatenate([rp1,rp1])
    dfSubOrder = pd.merge(dfSubOrder,dfCond,on='CondKey',how='left')
    dfSubOrder.to_csv('C:\Experiments\SentFill\SubDesigns\SubOrder' + str(subj) +'.csv')

dfSubOrder.groupby(['AttendGender', 'GenderLeft' , 'CondKey', 'NoiseCond','VideoCond']).count()
dfSubOrder.groupby(['AttendGender', 'GenderLeft' , 'RespKey', 'NoiseCond','VideoCond']).count()
dfSubOrder.groupby(['AttendGender', 'GenderLeft' , 'RespKey','CondKey', 'NoiseCond','VideoCond']).mean()

dfSortMeanPN = dfFsort.groupby(['PhonToNoise']).mean()
dfSortMeanPN['PhonToNoiseTime'] = (dfSortMeanPN['OffSampleNoise']-dfSortMeanPN['OnSampleNoise'])/float(48000)

dfSortMeanVB = dfFsort.groupby(['PhonVB']).mean()
dfSortMeanVB['PhonToNoiseTime'] = (dfSortMeanVB['OffSampleNoise']-dfSortMeanVB['OnSampleNoise'])/float(48000)