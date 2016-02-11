# -*- coding: utf-8 -*-
"""
Analysis script 

Created on Thu Jan 21 15:48:07 2016

@author: jrkerlin
"""
import numpy as np
from matplotlib.pyplot import *
import pandas as pd

import landkit
reload(landkit)
sc = landkit.SentCompare([['hello world']],[['hello mold']],'True')
lktable = landkit.LoadDict("test.csv")
sc = landkit.SentCompare(lktable['SentWords'],lktable['OrigResponse'],'True')

# Make pandas table with a
sentT = pd.DataFrame(lktable)

#Join the ngram and IPHoD info and "correctness"  at the word level
wordT = pd.concat([sc.tngram, sc.tphod], axis=1, join_axes=[sc.tngram.index])
wordT['HitIndex']= [y for x in sc.hits for y in x]
wordT['WordIndex']= [y for x in sc.hits for y,z in enumerate(x)]

#Table with phoneme Level info
phonT = sc.phonTable
bigPhonT = pd.concat([landkit.IndexFill(sentT,phonT['SentenceCount'],phonT['PhonemeCount']),landkit.IndexFill(wordT,phonT['WordCount'],phonT['PhonemeCount']),phonT], axis=1, join_axes=[phonT.index])
bigPhonT = pd.concat([landkit.IndexFill(wordT,phonT['WordCount'],phonT['PhonemeCount']),phonT], axis=1, join_axes=[phonT.index])
bigPhonT.to_csv('bigP.csv')
wordT.to_csv('wordT.csv')
#del(sc) #clear memory



#for snum,bools in enumerate(sc.hits_phonemes):
#   print sc.target_phonemes[snum]
#   print sc.source_phonemes[snum]
#   print bools
#
#sentenceACC = []
#for snum,bools in enumerate(sc.hits_phonemes):
#    print sc.target[snum]
#    print sc.source[snum]
#    booze = [int(boo) for boo in bools]
#    acc = sum(booze)/float(len(booze))
#    sentenceACC.append(acc)
#
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
#table = []
#for snum,bools in enumerate(sc.hits_phonemes):
#    booze = [int(boo) for boo in sc.hits[snum]]
#    sw = sc.source_matchWords[snum]
#    phons,wordIdx,word = zip(*sc.target_phonemes[snum])
#    wordACC = np.array(booze)[np.array(wordIdx)].tolist();
#    sourceword = np.array(sw)[np.array(wordIdx)].tolist();
#    table.extend(zip(phons,sc.source_matched[snum],bools,wordIdx,word,sourceword,wordACC))
#
#import pandas as pd
#pdtable = pd.DataFrame(table,columns=['TargetPhoneme','SourcePhoneme','PhonemeHitBool', 'WordIdx', 'TargetWord','SourceWord','wordACC'])
#
