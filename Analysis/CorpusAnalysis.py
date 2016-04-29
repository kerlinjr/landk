# -*- coding: utf-8 -*-
"""
Created on Tue Mar 08 10:46:59 2016

@author: jrkerlin

Gets all the TIMIT sentences

"""
import os
import fnmatch
import nltk 
import re
import inflect
import pandas as pd
import numpy as np
inflectEngine = inflect.engine() 

def normjoin(*arg):
    return os.path.normpath(os.path.join(*arg))
    
talkerPath = r'C:\TCDTIMIT\volunteersSmall'
outPath = normjoin(r'C:\TCDTIMIT\POS_tags')
pennpos =[]
sents = []
wordlist =[]
subjectNames = []
fileNames = []
df= pd.DataFrame()
regex = re.compile("[^a-zA-Z0-9 '-]")
folders = os.listdir(talkerPath)
for folder in folders:    
    path = os.path.join(talkerPath,folder,'straightcam')
    files = [p for p in os.listdir(path) if fnmatch.fnmatch(p,'*.txt')]
    for fname in files:
        words = []

        f = open(os.path.join(path,fname))
        for line in f:
            line = regex.sub('',line)
            linesplit = line.split(" ")[2].strip('\n').encode('utf8')
            for x,w in enumerate(linesplit):
                if w.isdigit():
                    linesplit[x] = inflectEngine.number_to_words(w)
            words.append(linesplit)
            #POS tagging through NLTK

        remapFunc = nltk.tag.mapping
        # Penn Treebank tagging through NLTK
        pennpos.extend([x[1] for x in nltk.pos_tag(words)])
        wordlist.extend(words)
        print(folder + ' ' + fname + ' POS loading...' )
        sents.extend([' '.join(words)]*len(words))
        subjectNames.extend([folder[1:]]*len(words))
        fileNames.extend([fname[:-4]]*len(words))            
#Remap Penn Tag to universal tagging
upos = [remapFunc.map_tag('en-ptb', 'universal', x) for x in pennpos]
taggedCorpus = pd.DataFrame(np.transpose([subjectNames,fileNames,sents,wordlist,pennpos,upos]),columns = ['Subject','File','Sentence','Word','PENNPOS','UPOS'])
taggedCorpus.to_csv(normjoin(outPath,'posTags.csv'))


           
        
        