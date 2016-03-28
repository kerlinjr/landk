# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 14:58:33 2016

@author: jrkerlin
"""

import os
import re
import pandas as pd
import numpy as np
def normjoin(*arg):
    return os.path.normpath(os.path.join(*arg))
    
rootPath = normjoin('C:/Experiments/JK302')
timings = pd.read_excel(normjoin(rootPath,'volunteer_labelfiles_parsed.xlsx'))

onset = []
offset = []
phon=[]
talker = []
sentenceID = []
firstCol = timings.iloc[:,0]
for x,line in enumerate(firstCol):
    if re.match('Q:*',str(line)):
        filename = line
        talk = result = re.search('volunteers/(.*)/Clips',line).group(1)
        sentID = result = re.search('straightcam/(.*).rec',line).group(1)
        print line
    elif str(line).isdigit():
        talker.append(talk)
        sentenceID.append(sentID)
        onset.append(timings.iloc[x,0])
        offset.append(timings.iloc[x,1])
        phon.append(timings.iloc[x,2])

timeTable = pd.DataFrame(np.transpose([talker,sentenceID,onset,offset,phon]),columns = ['Talker','SentenceID','Onset','Offset','Phoneme'])
timeTable.to_csv(normjoin(rootPath,'timeTable.csv'))
tt = timeTable[(timeTable['Talker']== talk) & (timeTable['SentenceID']== sentID)].reset_index()
speechRange = tt['Onset'].iloc[[1,-1]].values/float(10000000)*48000  
speechRange = np.round(speechRange) 