# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 09:42:11 2016

@author: jrkerlin

JK301 BigP Analysis

Analyses from BigP.csv table
"""
#Load Big P
import pandas as pd
import numpy as np
import os
from matplotlib.pyplot import *
from statsmodels.nonparametric.smoothers_lowess import lowess 

dfPT = pd.read_excel(os.path.normpath('C:\Experiments\JK302\Tables\Custom\TablesPhoneme.xlsx'),encoding='latin-1')
#PRP analysis
bigP = pd.DataFrame.from_csv(os.path.normpath(r'C:\Experiments\JK302\dataOut\bigP.csv'))
bigP = bigP[bigP['SoundCond'] == 'Babble']
#bigP = bigP[bigP['VideoCond'] == 'AV']
bigP['NewIdx']=np.arange(0,len(bigP))
bigP = bigP.set_index('NewIdx')
bigP['MaxPhonInSent']=bigP[['SentenceCount','PhonemeIndex']].groupby('SentenceCount').transform(lambda x: max(x))
bigP['DistenceToEndPhon'] = bigP['MaxPhonInSent']-bigP['PhonemeIndex']
allPhons = np.unique(dfPT['CMU Phonemes'])
prePhon = 5
postPhon = 8
xAxis = np.arange(-prePhon,postPhon+1)
isOver =  bigP['PhonemeIndex'] >= prePhon
isMinAhead =  bigP['DistenceToEndPhon'] >= postPhon

isAll = bigP['TargetPhoneme'].isin(allPhons)
isCorrect = bigP['PhonemeHitBool'].isin([False,True])

eventIndex = bigP[isAll & isOver & isMinAhead & isCorrect].index

lenIdx = len(eventIndex)
aPRP = np.zeros(prePhon+postPhon+1)
for idx in eventIndex:
    aPRP += bigP.iloc[idx-prePhon:idx+postPhon+1].loc[:,('PhonemeHitBool')]/float(lenIdx)*100
aPRP = aPRP-np.mean(aPRP[0:prePhon])    
#plot(aPRP)
f, axtup =subplots(7,6,figsize = (20,12),sharex='col',sharey='row')
ylim = [-10,10]
for x,phon in enumerate(allPhons):
    isPhon = isAll = bigP['TargetPhoneme'].isin([phon])
    eventIndex = bigP[isPhon & isOver & isMinAhead & isCorrect].index
    lenIdx = len(eventIndex)
    PRP = np.zeros(prePhon+postPhon+1)
    for idx in eventIndex:
        PRP += bigP.iloc[idx-prePhon:idx+postPhon+1].loc[:,('PhonemeHitBool')]/float(lenIdx)*100
    PRP = PRP-np.mean(PRP[0:prePhon])
    if lenIdx > 200:
        figPos = axtup[np.unravel_index(x,(7,6))]
        figPos.set_ylim(ylim)
        figPos.plot(xAxis,PRP-aPRP)
        #figPos.plot(xAxis,PRP)
        figPos.plot([0,0],[ylim[0],ylim[1]])
        figPos.set_title(phon)
err 
figure()
#Analysis of performance by Talker without noise
bigP = pd.DataFrame.from_csv(os.path.normpath(r'C:\Experiments\JK302\dataOut\bigP.csv'))
isClear = bigP['SoundCond'] == 'Clear'
isNoisy = bigP['SoundCond'] == 'Babble'
bigP = bigP[isNoisy]

#Accuracy by word frequency
bins = np.arange(-1,16,1)
names = [str(x) for x in bins[1:]]
bigP['Binned1LogGram'] = pd.cut(bigP['1LogGram'], bins, labels=names)
bigP[['PhonemeHitBool','Binned1LogGram','VideoCond']].groupby(['Binned1LogGram','VideoCond',]).mean().unstack().plot(kind='line')
bigP[['PhonemeHitBool','upos','VideoCond']].groupby(['upos','VideoCond',]).mean().unstack().plot(kind='line')

#Grouped by Talker
groupedTalker = bigP.groupby('Talker')
talkerMean = groupedTalker.mean()
talkerMean['PhonemeHitBool'].plot(kind='bar',figsize = (12,4))
#Grouped by subject
groupedSubject = bigP.groupby('Subject')
subjectMean = groupedSubject.mean()
subjectMean['PhonemeHitBool'].plot(kind='bar',figsize = (12,4))
#Grouped by word
groupedWord = bigP.groupby('WordCount')
wordMean = groupedWord.mean()
wordFirst = groupedWord.first()
wordMean['TargetWord'] = wordFirst['TargetWord']
wordMean['WordHit'] = wordMean['PhonemeHitBool'] == 1
#Grouped by type
groupedType = wordMean.groupby('TargetWord')

#Plot top 20 missed words
missedSorted = groupedType['WordHit'].apply(lambda x: np.sum(x == False)).sort_values(ascending = False)
missplot = missedSorted[0:20].plot(kind='bar',figsize = (12,4))
#Plot top 20 correct words
hitSorted = groupedType['WordHit'].apply(lambda x: np.sum(x == True)).sort_values(ascending = False)
hitplot = hitSorted[0:20].plot(kind='bar',figsize = (12,4))

#Plot top 20 most common  words in corpus
countSorted = groupedType['WordHit'].count().sort_values(ascending = False)
countplot = countSorted[0:20].plot(kind='bar',figsize = (12,4))

#Accuracy of top 20 most common words in english
meanType = groupedType.mean()
meanType['TypeCount'] = groupedType['WordHit'].count()
typeACC = meanType.sort_values('1LogGram',ascending = False)['WordHit']
accbar = typeACC[0:20].plot(kind='bar',figsize = (12,4))
accplot = typeACC.plot(kind='line',figsize = (12,4))


#typeACCFilt = typeACC
#filtered = lowess(typeACC.values,np.arange(0,len(typeACC)))
#typeACCFilt[0:] =  filtered[:,1]
#accplot = typeACCFilt.plot(kind='line',figsize = (12,4),color='black')

##Remove Talker s59F (practice talker)
#is59 = bigP['Talker'] == 's59F'
#bigP = bigP[np.invert(is59)]
