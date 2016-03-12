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


#Analysis of performance by speaker without noise
bigP = pd.DataFrame.from_csv(os.path.normpath(r'C:\TCDTIMIT\dataOut\JK301\bigP.csv'))
isClear = bigP['BabbleCond'] == 'Off'
isNoisy = bigP['BabbleCond'] == 'On'
bigP = bigP[isClear]
#Grouped by Speaker
groupedSpeaker = bigP.groupby('Speaker')
speakerMean = groupedSpeaker.mean()
speakerMean['PhonemeHitBool'].plot(kind='bar',figsize = (12,4))
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
typeACC = meanType.sort_values('SFreq',ascending = False)['WordHit']
accbar = typeACC[0:60].plot(kind='bar',figsize = (12,4))
accplot = typeACC.plot(kind='line',figsize = (12,4))
typeACCFilt = typeACC
filtered = lowess(typeACC.values,np.arange(0,len(typeACC)))
typeACCFilt[0:] =  filtered[:,1]
accplot = typeACCFilt.plot(kind='line',figsize = (12,4),color='black')

##Remove Speaker s59F (practice talker)
#is59 = bigP['Speaker'] == 's59F'
#bigP = bigP[np.invert(is59)]
