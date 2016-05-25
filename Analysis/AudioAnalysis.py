# -*- coding: utf-8 -*-
"""
Created on Tue Mar 08 10:46:59 2016

@author: jrkerlin

Gets all the TIMIT sentences

"""
import os
import fnmatch
import re
import pandas as pd
import numpy as np
import scipy.io.wavfile
import math
import landkit 

def normjoin(*arg):
    return os.path.normpath(os.path.join(*arg))

def rms(array):
    return np.sqrt(np.mean(np.square(array)))
    
def amp2db(scalar):
    return 20 * math.log10(scalar)


        


    
talkerPath = r'C:\TCDTIMIT\volunteersSmall'
outPath = normjoin(r'C:\TCDTIMIT\Tables')
ttPath = normjoin(r'C:\TCDTIMIT\Tables\timeTable_r1.csv')




timeTable = pd.DataFrame.from_csv(ttPath)
timeTable['Talker'] = ['s'+str(x) for x in timeTable['Talker']]
audioTable = pd.DataFrame(index = [],columns =timeTable.columns)
audioTable['SpeechRMS'] = []
audioTable['FileID'] = []
subjectNames = []
fileNames = []
volume =[]
df= pd.DataFrame()
regex = re.compile("[^a-zA-Z0-9 '-]")
volume =[]
folders = os.listdir(talkerPath)
fCount = 0
FileID = []
volGrouped=[]
for folder in folders:    
    path = os.path.join(talkerPath,folder,'straightcam')
    files = [p for p in os.listdir(path) if fnmatch.fnmatch(p,'*.wav')]
    for fname in files:
        tt = timeTable[(timeTable['Talker']== folder) & (timeTable['SentenceID']== fname[:-4])].reset_index()
#        tt = tt[tt['Phoneme'] != 'sil']
        tmp,wav = scipy.io.wavfile.read(normjoin(path,fname))
        wav = wav.astype('float32')
        volume=[]
        for x in np.arange(0,len(tt)):
            speechRange = tt[['Onset','Offset']].iloc[x,:].values/float(10000000)*48000  
            speechRange = np.round(speechRange).astype('int')
            phon = str(tt[['Phoneme']].iloc[x][0]).upper()
            onset = speechRange[0]
            offset = speechRange[1]
            vol = rms(np.array(wav[speechRange[0]:speechRange[1]]))
            volume = np.append(volume,vol)
            #volSent = np.append(volSent,pd.DataFrame(phon,onset,offset,vol)) 
        print(folder + ' ' + fname + ' Volume Tagging...' )
        #volGrouped.append(volSent)
 
        tt['FileID'] = fCount
        tt['SpeechRMS'] = volume
        audioTable = pd.concat([audioTable,tt])
        fCount += 1 
        
audioTable.to_csv(os.path.normpath(r'C:\TCDTIMIT\Tables\audioTable_r1.csv'))

#Match HTK forced alignments to landkit phonemes 
taggedCorpus = pd.DataFrame.from_csv(normjoin(outPath,'posTags_r1.csv'))
justSent = taggedCorpus.groupby(['Subject','File']).first().reset_index()
sc = landkit.SentCompare(list(justSent['Sentence']),list(justSent['Sentence']),False,normjoin('C:\Experiments\JK302'))
sc.GeneratePhonemes()

audioTable = pd.DataFrame.from_csv(os.path.normpath(r'C:\TCDTIMIT\Tables\audioTable_r1.csv'))

def source2target(sourceList,targetList,sourceVal,fillOpt='Neg1'):
    import difflib
    
    d = difflib.Differ()
    list(d.compare(sourceList,targetList))
    instruct = [x[0] for x in list(d.compare(sourceList,targetList))]
    
    c = 0
    while c < len(instruct)-1:
        if instruct[c] == '-' and instruct[c+1] == '+':
            instruct[c] = ' '
            del instruct[c+1]
        c +=1
    

    cnt= 0
    targetVal = []
    for c in instruct:
       if c == ' ':
           targetVal.append(sourceVal[cnt])
           cnt += 1
       elif c == '+':
           if fillOpt == 'Neg1': #Fill missing items with -1
               targetVal.append(-1)
           elif fillOpt == 'take1back': # Take the most recent preceding value if it exists, else take the first value
               if cnt < len(sourceVal):
                   targetVal.append(sourceVal[cnt])
               else:
                   targetVal.append(sourceVal[cnt-1])
           elif fillOpt == 'blankline': # Take the most recent preceding value if it exists, else take the first value
               targetVal.append('-')
       elif c == '-':
           cnt += 1
    return targetVal      

#sourceList = Sequence(['a','b','a','c','b','f','g','i','j'])
#targetList = Sequence(['j','a','b','a','b','q','f','y','i','k'])
#sourceVal = [1,2,3,4,5,6,7,8,9]    
tt = audioTable[audioTable['Phoneme'] != 'sil']
rmsVal = []
onsetVal = []
offsetVal = []
onsetVal = []
phonVal = []
talkerVal = []
sentIDVal = []
FileIDVal = []
targetVal = []
wordVal = []
wordIdxVal = []
phonemeIndex =[]
for x,tlist in enumerate(sc.target_phonemes):
    sourceList = tt.loc[tt['FileID'] == x,'Phoneme']
    sourceList = [y.upper() for y in sourceList] 
    targetList,wordIdxList,wordList = zip(*tlist)
    targetList = [str(z) for z in targetList] 
    wordList = [str(z) for z in wordList] 
    sourceVal = list(tt.loc[tt['FileID'] == x,('SpeechRMS')])   
    rmsVal.extend(source2target(sourceList,targetList,sourceVal,fillOpt='take1back'))    
    
    sourceVal = list(tt.loc[tt['FileID'] == x,('Onset')])
    onsetVal.extend(source2target(sourceList,targetList,sourceVal,fillOpt='take1back'))
    sourceVal = list(tt.loc[tt['FileID'] == x,('Offset')])
    offsetVal.extend(source2target(sourceList,targetList,sourceVal,fillOpt='take1back'))
    sourceVal = list(tt.loc[tt['FileID'] == x,('Phoneme')])
    phonVal.extend(source2target(sourceList,targetList,sourceVal,fillOpt='blankline'))
    sourceVal = list(tt.loc[tt['FileID'] == x,('Talker')])
    talkerVal.extend(source2target(sourceList,targetList,sourceVal,fillOpt='take1back'))
    sourceVal = list(tt.loc[tt['FileID'] == x,('SentenceID')])
    sentIDVal.extend(source2target(sourceList,targetList,sourceVal,fillOpt='take1back'))
    sourceVal = list(tt.loc[tt['FileID'] == x,('FileID')])
    FileIDVal.extend(source2target(sourceList,targetList,sourceVal,fillOpt='take1back'))
    targetVal.extend(targetList)
    wordVal.extend(wordList)
    wordIdxVal.extend(wordIdxList)
    phonemeIndex.extend(np.arange(0,len(targetList)))
    if np.mod(x,100) == 0:
        print('Sentence '+str(x)+' Loading...')
onsetValPnts = [np.round(x/float(10000000)*48000).astype('int') for x in onsetVal]   
offsetValPnts = [np.round(x/float(10000000)*48000).astype('int') for x in offsetVal]       
audioTableTM = pd.DataFrame(np.transpose([FileIDVal,talkerVal,sentIDVal,onsetValPnts,offsetValPnts,rmsVal,phonVal,targetVal,phonemeIndex,wordVal,wordIdxVal]),columns =['FileID','Talker','SentenceID','OnsetSample','OffsetSample','SpeechRMS','HTKPhoneme','TargetPhoneme','PhonemeIndex','Word','WordIndex'])       
audioTableTM.to_csv(normjoin(outPath,'audioTableTM.csv'))

#audioTableTM.rename(columns={'FileCount':'FileID'}, inplace=True)
#audioTableTM['Talker'] = ['s'+str(x) for x in audioTableTM['Talker']]
#atm = audioTableTM.groupby(['Talker','SentenceID']).first().reset_index()
#bigP= pd.merge(bigP,atm, how='left', on=['Talker','SentenceID'])
           