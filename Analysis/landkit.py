# -*- coding: utf-8 -*- 
"""
Land Kit Modules
(Currently only works with 32 bit python)
Created on Wed Jan 20 16:25:54 2016

These functions will be used to load, preprocess and analyse Land Data 
@author: jrkerlin

"""
import sys
sys.path.append(r'C:\Users\jrkerlin\Documents\GitHub\landk\Analysis')
import nltk
import enchant #(will not install on 64-bit python)
from alignment.sequence import Sequence 
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner
import numpy as np
import pandas as pd
import requests
import inflect
import time
import re, collections

def norvigTrain(filename=[]):
    def words(text): return re.findall('[a-z]+', text.lower()) 

    def train(features):
        model = collections.defaultdict(lambda: 1)
        for f in features:
            model[f] += 1
        return model
    if filename:
        NWORDS = train(words(file(filename).read()))
    else:
        WORDLIST = ' '.join(nltk.corpus.words.words())
        NWORDS = train(words(WORDLIST))
        
    return NWORDS
   
def norvig(text,NWORDS):
    
    alphabet = 'abcdefghijklmnopqrstuvwxyz'

    def edits1(word):
       splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
       deletes    = [a + b[1:] for a, b in splits if b]
       transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
       replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
       inserts    = [a + c + b     for a, b in splits for c in alphabet]
       return set(deletes + transposes + replaces + inserts)

    def known_edits2(word):
        return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

    def known(words): return set(w for w in words if w in NWORDS)

    def correct(word):
        candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
        #return max(candidates, key=NWORDS.get)
        return list(candidates)
    return correct(text)


class SentCompare:
    """Class for the lexical and phonetic comparison of sentences


    Attributes:
        target: A list of sentences to which responses will be aligned
        source: A list of sentences to align to target sentences. 
            Must be the same length as target sentences. 
    Returns:
        A Pandas tabel of relevent information, if full_execute is true        
    """
    def __init__(self,target=[],source=[],full_execute=False):
        #Turn string inputs to list inputs for success with enumerate loops
        if type(target) == str:
            target = [target]
        if type(source) == str:
            source = [source]  
            
        self.target = target
        self.source = source
        self.spelldict = nltk.corpus.words.words()
        self.phondict = nltk.corpus.cmudict.entries()
        self.tableFolder = r'C:/TCDTIMIT/Tables/'
        if full_execute == True:
            print 'go'
            self.SpellCorrect()
            self.ScoreWords()
            self.GeneratePhonemes()
            self.ScorePhonemes()
            self.GeneratePhonemeTable()
            self.SentenceAnalysis()
            
    def SpellCorrectNorvig(self,NWORDS):
        """Corrects the spelling of the source sentences using
        Norvig spell checking.
        
        If a spell checked suggestion can be found in the target text, that suggestion is used.
        If not, the first suggestion is used.
        All words are forced to lowercase.
           
        Attributes:
            source (list): The spell corrected version of the source sentence list
        
        Note:
            This spell checker does not tokenize any input words 
            other than to parse based on blank space, remove punctuation/non-English chars and replace digits with words 
            It is not designed to work with non-word lemma (i.e. "n't")
        """ 
#        d = enchant.Dict("en_US") #Use the American Enchant dictionary        
        
        source = self.source
        target = self.target
        sourcecorr = []
        p = inflect.engine()
        rcnt =enumerate(source)
        for sent in source:
            wf = ''
            #Make lowercase and strip off all characters except 26 letter alpha-numeric, "'",or " "
            allowedChars = set(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',"'"," ","-",'1','2','3','4','5','6','7','8','9','0'])               
            sent = ''.join(ch for ch in sent.lower() if ch in allowedChars)
            sent.replace("-", " ")
            sp = sent.split() 
            rint =rcnt.next()
            for word in sp:    
                #Replace digits with words

                if word.isdigit():
                    word = p.number_to_words(word)
                nword = norvig(word,NWORDS)
                if nword[0] != word and not word in self.target[rint[0]].split(): 
                    replacefound = False
                    for sug in nword: 
                        #loop through suggestions to find word match with target sentence
                        #replace and quit looking if target match is found
                        if sug in target[rint[0]].split():  
                            wf = wf + ' ' + sug.lower()
                            replacefound = True
                            #print(word)
                            #print(sug)
                            break
                        #If no match with target is found, replace with first suggestion    
                    if replacefound == False:
#                        if nword:
#                            wf = wf + ' ' + nword[0].lower()
#                        else:
                            wf = wf + ' ' + word.lower()
                        #print(word)
                        #print(d.suggest(word)[0])
                #If spelling correct, keep the original word, lowercased        
                else:
                    wf = wf + ' ' + word.lower()
            sourcecorr.append(wf[1:])
        self.source = sourcecorr

      
 
    def SpellCorrect(self):
        """Corrects the spelling of the source sentences using
        Enchant spell checking.
        
        If a spell checked suggestion can be found in the target text, that suggestion is used.
        If not, the first suggestion is used.
        All words are forced to lowercase.
           
        Attributes:
            source (list): The spell corrected version of the source sentence list
        
        Note:
            This spell checker does not tokenize any input words 
            other than to parse based on blank space, remove punctuation/non-English chars and replace digits with words 
            It is not designed to work with non-word lemma (i.e. "n't")
        """
        d = enchant.Dict("en_US") #Use the American Enchant dictionary        
        p = inflect.engine()
        sourcecorr = []
        rcnt =enumerate(self.source)
        for sent in self.source:
            wf = ''
            #Make lowercase and strip off all characters except 26 letter alpha-numeric, "'",or " "
            allowedChars = set(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',"'"," ","-",'1','2','3','4','5','6','7','8','9','0'])               
            sent = ''.join(ch for ch in sent.lower() if ch in allowedChars)
            sent.replace("-", " ")
            sp = sent.split() 
            rint =rcnt.next()
            for word in sp:    
                #Replace digits with words
                if word.isdigit():
                    word = p.number_to_words(word)
                if d.check(word) == False and not word in self.target[rint[0]].split(): 
                    replacefound = False
                    for sug in d.suggest(word): 
                        #loop through suggestions to find word match with target sentence
                        #replace and quit looking if target match is found
                        if sug in self.target[rint[0]].split():  
                            wf = wf + ' ' + sug.lower()
                            replacefound = True
                            #print(word)
                            #print(sug)
                            break
                        #If no match with target is found, replace with first suggestion    
                    if replacefound == False:
                        if d.suggest(word):
                            wf = wf + ' ' + d.suggest(word)[0].lower()
                        else:
                            wf = wf + ' ' + word.lower()
                        #print(word)
                        #print(d.suggest(word)[0])
                #If spelling correct, keep the original word, lowercased        
                else:
                    wf = wf + ' ' + word.lower()
            sourcecorr.append(wf[1:])
        self.source = sourcecorr

            
    def ScoreWords(self):
        """Aligns the words of the source sentence to match the target sentence
        to determine hit vs missed words
    
        Returns:
           hits (nested list): The target [0] and source [1] sentences in a nested list 
    
        Note:
        Modified from Eser Aygün (https://pypi.python.org/pypi/alignment/1.0.9)
        """
        target = self.target
        source = self.source
        self.source_matchWords = []  
        hits=[]
        wscore = np.empty(0)
        for tnum,tsent in enumerate(target):
            ssent = source[tnum]
            # Create sequences to be aligned.
            a = Sequence(tsent.split())
            b = Sequence(ssent.split())
            
            # Create a vocabulary and encode the sequences.
            v = Vocabulary()
            aEncoded = v.encodeSequence(a)
            bEncoded = v.encodeSequence(b)
            
            # Create a scoring and align the sequences using global aligner.
            scoring = SimpleScoring(5, -1)
            aligner = GlobalSequenceAligner(scoring, -1)
            score, encodeds = aligner.align(aEncoded, bEncoded, backtrace=True)
            encoded = encodeds[0]
            
            #Score based only on hits vs misses, insertions are ignored
            notInsert = encoded[:][0] != 0
            nonInsertMatched = encoded[notInsert][:]
            
            #Find the alignment in the target sequence
            aSeq = nonInsertMatched[:][0]
            bSeq = nonInsertMatched[:][1]
            
            #Label all items not aligned to the target as false
            hitlist = []
            x = 0
            for x in range(0,len(aEncoded)-len(aSeq)+1):
                aChunk = aEncoded[x:x+len(aSeq)]
                #print aChunk
                if sum(aChunk-aSeq) == 0:
                    break
            hitlist.extend([False]*(x))    
            hitlist.extend(list(aSeq-bSeq == 0))
            hitlist.extend([False]*(len(aEncoded)-x-len(aSeq)))
            #Export the target aligned words of the source sequence
            bWords = np.zeros(len(aEncoded),int)
            bWords[x:x+len(bSeq)] = bSeq
            bWordOut = np.array(v.elements())[bWords].tolist()
            hits.append(hitlist)
            iwscore = sum(hitlist)*100/float(len(hitlist))
            wscore = np.hstack([wscore,iwscore])
            print bWordOut 
            self.source_matchWords.append(bWordOut)            
            self.hits = hits
            self.wscore = wscore
               
    def GeneratePhonemes(self, dictPath=' ',dictFileName = ' '):   
        """Generates a list of phonemes from each sentence, and codes the word to which each phoneme belongs
    
        Returns:
           target_phonemes (nested list,tuple): list of phonemes, word position in sentence and word for each target sentence
           source_phonemes (nested list,tuple): list of phonemes, word position in sentence and word for each source sentence
 
        """
        missKeyFile = r'C:\TCDTIMIT\missingkeys\missingkeys.csv'
        if dictPath !=' ':
            prondict = {}
            with open(dictPath + dictFileName) as f: #open dictionary
                for line in f:
                    (key, val) = line.split(' ',1) 
                    key = key.lower()
                    prondict[key] = val.split()
                    for pnum,phon in enumerate(prondict[key]): #remove vowel varient coding
                        if  len(phon) > 2:
                            prondict[key][pnum] = phon[:-1]
        else: #Use the American English CMU dictionary by default 
            prondict = nltk.corpus.cmudict.dict()
            for key in prondict.keys():
                prondict[key] = prondict[key][0]
                for pnum,phon in enumerate(prondict[key]): #remove vowel varient coding
                    if  len(phon) > 2:
                        prondict[key][pnum] = phon[:-1]            
        

    



        # Collect the phonemes, word position index and word list for both the target and source
        # Collect the total word count of the target
        self.target_phonemes = []  
        self.source_phonemes = []
        self.phonCount = []
        self.wordCount = []
        self.sentCount = []
        wCnt = 0
        pCnt = 0
        sCnt = 0
        
        allTargetWords = [ word for tsent in self.target for word in tsent.split()]
        allSourceWords = [ word for tsent in self.source for word in tsent.split()]
        
        #Find the missing dictionary keys
        missingkeys =[]
        for w in allSourceWords:
            if not prondict.has_key(w):
                missingkeys.append(w)
        for w in allTargetWords:
            if not prondict.has_key(w):
                missingkeys.append(w)
        if missingkeys:
            
            pd.DataFrame(missingkeys)[0].to_csv(missKeyFile,index = False)        
            #Get the missing keys phonemes from Logios
            url = 'http://www.speech.cs.cmu.edu/cgi-bin/tools/logios/lextool.pl'
            r = requests.post(url, files={'wordfile': open(missKeyFile, 'rb')})
            starthtml = r.text.find('DICT')+5
            endhtml = r.text.find('-->')-2
            inURL = r.text[starthtml:endhtml:1]
            r = requests.get(inURL)
            logiosIn = [x.strip().split("\t") for x in r.text.strip().split("\n")]
            for x,y in enumerate(logiosIn):
                logiosIn[x][0] = logiosIn[x][0].lower()              
            prondict.update(logiosIn)  
#         # Add missing words to the phoneme dictionary (from Logios)
#        misskeys = pd.read_csv('missingkeys.dict','\t',header=None,index_col=0,names=['Phonemes'])
#        misskeys['Lower'] = [x.lower() for x in list(misskeys.index)]
#        misskeys = misskeys.set_index(['Lower'])
#        missdict = misskeys.to_dict()['Phonemes']
         
         #Add missing keys to the dictionary                    
                
        #Generate Phoneme list    
        for snum,tsent in enumerate(self.target):
            ssent = self.source[snum] 
            self.source_phonemes.append([(phon,wnum,word) for wnum,word in enumerate(ssent.split()) for pnum,phon in enumerate(prondict[word])])
            phon,wnum,word,wordCount = zip(*[(phon,wnum,word,wnum+wCnt) for wnum,word in enumerate(tsent.split()) for pnum,phon in enumerate(prondict[word])])
            self.target_phonemes.append(zip(phon,wnum,word))
            wn = [wn for wn,wd in enumerate(tsent.split())]
            self.wordCount.append(wordCount)
            self.phonCount.append([pCnt+num for num,tmp in enumerate(phon)])
            self.sentCount.append([sCnt for num,tmp in enumerate(phon)])
            wCnt = wCnt + len(wn)
            pCnt = pCnt + len(phon)
            sCnt = sCnt + 1
                
    def ScorePhonemes(self,source =[],target =[]):
        """Compare the phonemes of a source and target sentence and determine 
        which of the target items were correctly transcribed
    
        Returns:
            hits_phonemes (nested list): list of bools corresponding to the accuracy
            of each phoneme in the target list for each sentence
        Note:
        This scoring method has no word accuracy awareness. Phonemes from correctly input
        words may wind up as labeled wrong ( i.e. target:"with the" source: "with a" alignement: )
        Modified from Eser Aygün (https://pypi.python.org/pypi/alignment/1.0.9)        
        """
        if not source:
            source = self.source_phonemes
        if not target:    
            target = self.target_phonemes
        
        self.source_matched =[]            
        hits=[]
        for x,ttup in enumerate(target):
            tphon,twordnum,tword =  zip(*ttup)
            stup = source[x]
            sphon,swordnum,sword =  zip(*stup)
            # Create sequences to be aligned.
            a = Sequence(tphon)
            b = Sequence(sphon)
            
            # Create a vocabulary and encode the sequences.
            v = Vocabulary()
            aEncoded = v.encodeSequence(a)
            bEncoded = v.encodeSequence(b)
            
            # Create a scoring and align the sequences using global aligner.
            scoring = SimpleScoring(2, -1)
            aligner = GlobalSequenceAligner(scoring, -2)
            score, encodeds = aligner.align(aEncoded, bEncoded, backtrace=True)
            encoded = encodeds[0]
            
            #Score based only on hits vs misses, insertions are ignored
            notInsert = encoded[:][0] != 0
            nonInsertMatched = encoded[notInsert][:]
            
            #Find the alignment in the target sequence
            aSeq = nonInsertMatched[:][0]
            bSeq = nonInsertMatched[:][1]
            
            #Label all items not aligned to the target as false
            hitlist = []
            x = 0
            for x in range(0,len(aEncoded)-len(aSeq)+1):
                aChunk = aEncoded[x:x+len(aSeq)]
                #print aChunk
                if sum(aChunk-aSeq) == 0:
                    break
            hitlist.extend([False]*(x))    
            hitlist.extend(list(aSeq-bSeq == 0))
            hitlist.extend([False]*(len(aEncoded)-x-len(aSeq)))
            #Export the target aligned phonemes of the source sequence
            bPhons = np.zeros(len(aEncoded),int)
            bPhons[x:x+len(bSeq)] = bSeq
            bPhonOut = np.array(v.elements())[bPhons].tolist()
            hits.append(hitlist)
            self.source_matched.append(bPhonOut)
            self.hits_phonemes = hits
            
    def SentenceAnalysis(self):
        """Create a table of sentence level analysis
    
        """  
        target = self.target
        targetp = self.target_phonemes
        maxWord = max(self.phonTable['WordCount'])

        #Load Irvine Phonotactic Dictionary
        phod2 = pd.read_csv(self.tableFolder + r'IPhODv2.0_REALS\IphOD2_Words.csv')
        words = list(phod2['Word'])
        words = [x.lower() for x in words]
        phod2['Word'] = words
        


        #phod2 = phod2.set_index(phod2['UnTrn'])
        #Make an empty DataFrame with the right size and labels
        #tphod = phod2.loc[phod2['UnTrn'].isin(['thisinstthere'])] 
        #wordpd = pd.DataFrame(columns = ['WordCount'])


        #Load n word frequencies
        ngramf1 =  pd.read_table(self.tableFolder + r'Norvig\count_1w.txt',header=None,names=['Word','WordFreq',])
        ngramf2 = pd.read_table(self.tableFolder + r'COCAFree\Ngram2.txt',header=None,names=['BigramFreq','Bi0','Bi1'])
        ngramf3 = pd.read_table(self.tableFolder + r'COCAFree\Ngram3.txt',header=None,names=['TrigramFreq','Tri0','Tri1','Tri2'])
        min0 = min(ngramf1['WordFreq'])
        min1 = min(ngramf2['BigramFreq'])
        min2 = min(ngramf3['TrigramFreq'])
        
#       #Use phonemes for IPhoD lookup
#        wCnt = 0 
#        tphod = pd.DataFrame(columns = phod2.columns, index = range(0,maxWord+1))
#        for tnum,tsent in enumerate(target):
#            phon,wordIdx,word = zip(*targetp[tnum])
#            phonList = GetMatched(phon,wordIdx)  
#            #Load in relevent item using phonetic spelling from phod list
#            for i in range(0,len(phonList)):
#                
#                phodForm =''
#                for p in phonList[i]:
#                    phodForm=phodForm+p+'.'
#                phodForm = phodForm[:-1]
#                lines = phod2.loc[phod2['UnTrn'].isin([phodForm])]
#                if len(lines):
#                    tphod.iloc[wCnt] =lines.iloc[0]                     
#                wCnt = wCnt+1 
        #Use words for IPhoD lookup
        wCnt = 0 
        tphod = pd.DataFrame(columns = phod2.columns, index = range(0,maxWord+1))
        for tnum,tsent in enumerate(target):
            phon,wordIdx,word = zip(*targetp[tnum])
            wordList = tsent.split()
            phonList = GetMatched(phon,wordIdx)
            #Load in relevent item using phonetic spelling from phod list
            for i,w in enumerate(wordList):
                phodForm =''
                for p in phonList[i]:
                    phodForm=phodForm+p+'.'
                phodForm = phodForm[:-1]
                # Find matching words
                lines = phod2.loc[phod2['Word'].isin([w])]
                # Find matching pronunciations
                lines = lines.loc[lines['UnTrn'].isin([phodForm])]
                if len(lines):
                    tphod.iloc[wCnt] =lines.iloc[0]                     
                wCnt = wCnt+1         
        
        
        wCnt = 0 
        wordsum =[] 
        bisum = []   
        trisum = []
        for tnum,tsent in enumerate(target):     
            #Load in relevent ngram frequencies using orthographic spelling
            wordList = tsent.split()
            #unigram(word) frequency analysis  
            wordvals = np.zeros(len(wordList))
            
            for w,word in enumerate(wordList):
                nmatch0 =  ngramf1[ngramf1['Word'].isin([word])];
                if nmatch0.empty:
                    wordvals[w] = np.log(min0) 
                else:                   
                    wordvals[w]  = np.log(nmatch0['WordFreq'].values[0])
            wordsum.extend(wordvals)

            #bigram frequency analysis
            bigrams = list(nltk.ngrams(wordList,2))
            bivals = np.ones(len(bigrams)+2)*np.log(min1)
            for biidx,bi in enumerate(bigrams):
                nmatch0 = ngramf2[ngramf2['Bi0'].isin([bi[0]])];
                nmatch1 = nmatch0[nmatch0['Bi1'].isin([bi[1]])];
                if nmatch1.empty:
                    bivals[biidx+1] = np.log(min1)
                else:
                    bivals[biidx+1]  = np.log(nmatch1['BigramFreq'].values[0])
            bisum.extend([sum(x) for x in list(nltk.ngrams(bivals,2))])
            # trigram frequency analysis
            trigrams = list(nltk.ngrams(wordList,3))
            trivals = np.ones(len(trigrams)+4)*np.log(min2)
            for triidx,tri in enumerate(trigrams):
                nmatch0 = ngramf3[ngramf3['Tri0'].isin([tri[0]])];
                nmatch1 = nmatch0[nmatch0['Tri1'].isin([tri[1]])];
                nmatch2 = nmatch1[nmatch1['Tri2'].isin([tri[2]])];
                if nmatch2.empty:
                    trivals[triidx+2] = np.log(min2)
                else:
                    trivals[triidx+2]  = np.log(nmatch2['TrigramFreq'].values[0])
            trisum.extend([sum(x) for x in list(nltk.ngrams(trivals,3))])
            print 'trial '+str(tnum)
        #Export the summed log-transformed occurences of n-gram occurances for each word     
        tngram = pd.DataFrame({ '1LogGram' : wordsum,'2LogGram' : bisum,'3LogGram' : trisum} )            
        self.tphod = tphod        
        self.tngram = tngram        
        
        

        

    
    def GenerateWordTable(self):
        """Makes a Pandas table out of all useful word variables from the class structure
    
        Returns:
            wordTable (pandas table) A Pandas table of relevant variables
        
        Notes: 
            NEEDS WORK
        """

    def GenerateSentenceTable(self):
        """Makes a Pandas table out of all useful sentence variables from the class structure
    
        Returns:
            sentTable (pandas table) A Pandas table of relevant variables
        
        Notes: 
            NEEDS WORK
        """
            
    def GeneratePhonemeTable(self):
        """Makes a Pandas table out of all useful phoneme variables from the class structure
    
        Returns:
            phonTable (pandas table) A Pandas table of relevant variables
        """
        table = []
        for snum,bools in enumerate(self.hits_phonemes):
            booze = [int(boo) for boo in self.hits[snum]]
            sw = self.source_matchWords[snum]
            phons,wordIdx,word = zip(*self.target_phonemes[snum])
            wordACC = np.array(booze)[np.array(wordIdx)].tolist()
            sourceword = np.array(sw)[np.array(wordIdx)].tolist() 
            table.extend(zip(self.phonCount[snum],range(0,len(phons)),phons,self.source_matched[snum],bools,self.wordCount[snum],wordIdx,word,sourceword,wordACC,self.sentCount[snum]))

        self.phonTable = pd.DataFrame(table,columns=['PhonemeCount','PhonemeIndex','TargetPhoneme','SourcePhoneme','PhonemeHitBool','WordCount', 'WordIdx', 'TargetWord','SourceWord','WordACC','SentenceCount'])

def IndexFill(pdt,origIdx,newIdx):
    """Generates a new Pandas table (pdt) based on the indexes
       Useful for repeating the values of items of a collapsed table to match a table of the length of expanded indexVar
       
    Returns:
        pdt (pandas table): A pandas table with the additional variables 
       
    """      
    pdto = pdt.iloc[origIdx]
    pdto.index = newIdx
    return pdto
   
def GetMatched(var,indexVar):
    """Get the values of variable var for the index variable from 0 to n and 
        drop each value list into a nested list of length max(indexVar)  
    
    Returns:
        new nested Numpy array with all instances at each index 
    Example:
        var = ['a','b','c','d']
        indexVar = [0,1,1,2]
        GetMatched(var,indexVar) returns [['a'],[b','c']['d']]
    """    
    return [np.array(var)[np.where(np.array(indexVar) == i)[0]] for i in list(set(indexVar))]

       
