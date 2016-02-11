# -*- coding: utf-8 -*-
"""
Example LandKit Script  

Created on Thu Jan 21 15:48:07 2016

@author: jrkerlin
"""
import numpy as np
from matplotlib.pyplot import *
import landkit
reload(landkit)
lktable = landkit.LoadDict("test.csv")
sc = landkit.SentCompare(lktable['SentWords'],lktable['OrigResponse'])
sc.SpellCorrect()
sc.ScoreWords()
sc.GeneratePhonemes()
sc.ScorePhonemes()
sc.GeneratePhonemeTable()
sc.SentenceAnalysis()

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
