# -*- coding: utf-8 -*-
"""Creates a hundred, ten second 8-speaker Babble stimuli from the TCDTIMIT SX wav files of all speakers
Each wav file is normalized at an RMS value of 40 (dtype int16)
@author: jrkerlin
"""

from __future__ import division 
import numpy as np
import scipy.io.wavfile
import os
import glob
import matplotlib
from numpy import mean, sqrt, square

def MakeBabble(sourcefolders,outputPath,fileRegEx,outputName):
    #Make Babble Directiory if does not exist
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
                #Dont overwrite files, skip if file exists
    if os.path.isfile (outputPath + '\\' + outputName): 
        print "Babble already exists"
        return       
    fs = 48000    
    babble = np.zeros(fs*10,dtype='float32')      
    for x,sf in enumerate(sourceFolders):    
        potentialFiles = np.array(glob.glob(sf + '\\' +fileRegEx)) 
        pickFiles = potentialFiles[np.random.random_integers(0,len(potentialFiles)-1,6)]
        tempMat = np.array([],dtype='float32')
        for y,pf in enumerate(pickFiles):
            tmp,wav = scipy.io.wavfile.read(pf)
            wav = wav.astype('float32')
            #normalize each file to RMS 40
            wav = (40/rms(wav)*wav)
            tempMat = np.hstack([tempMat,wav])
        #Make babble last for 10 seconds, starting from some point between 2 and 8 seconds into the concatenated sound files      
        startPoint = np.random.choice(range(2*fs,fs*8-1))  
        babble = babble + tempMat[startPoint:startPoint+fs*10]
        #Write 
    scipy.io.wavfile.write(outputPath + '\\' + outputName, fs,babble.astype('int16'))

def rms(array):
    return sqrt(mean(square(array)))
        
#Start script
#Set paths and speakers
stimPath = 'C:/TCDTIMIT/volunteersFull/'
speakers = os.listdir('C:/TCDTIMIT/volunteersFull/')
females = np.array([spkr for spkr in speakers if spkr[-1] == 'F'])
males = np.array([spkr for spkr in speakers if spkr[-1] == 'M'])


sourceFolders = [os.path.normpath(stimPath + spkr + '/straightcam/') for spkr in selSpeakers]
numBabbleFiles = 100
for i in range(0,numBabbleFiles): 
    #Make 8 speaker babble (4 male, 4 female)
    rand4f = females[np.random.random_integers(0,len(females)-1,4)]
    rand4m = males[np.random.random_integers(0,len(males)-1,4)]
    selSpeakers = np.concatenate([rand4f,rand4m])
    outputPath = 'C:/TCDTIMIT/Babble/'
    fileRegEx = r'sx*.wav'
    outputName = 'babble' + str(i) + '.wav'
    MakeBabble(sourcefolders,outputPath,fileRegEx,outputName)    


 
