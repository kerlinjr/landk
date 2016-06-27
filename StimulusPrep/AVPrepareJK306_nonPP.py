"""Audio visual preparation of TCD-TIMIT sentences for EEG

PsychoPy movie presentation dependencies:

Movie2 does require:
~~~~~~~~~~~~~~~~~~~~~

1. Python OpenCV package (so openCV libs and the cv2 python interface).
    *. For Windows, a binary installer is available at http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv
    *. For Linux, it is available via whatever package manager you use.
    *. For OSX, ..... ?
2. VLC application. Just install the standard VLC (32bit) for your OS. http://www.videolan.org/vlc/index.html

Movie3 does require:
~~~~~~~~~~~~~~~~~~~~~

moviepy (which requires imageio, Decorator). These can be installed
(including dependencies) on a standard Python install using `pip install moviepy`
imageio will download further compiled libs (ffmpeg) as needed

"""


from __future__ import division

#pyo.pa_get_input_devices()
#prefs.general['audioLib'] = ['pygame']
#prefs.general['audioDriver'] = ['SPDIF (RME HDSP 9652)'] #kills none spdif microphone

''' Doesnt work yet
from psychopy import parallel
parallel.PParallelInpOut32
parallel.setPortAddress(0x03F8)
parallel.setData(255)
core.wait(.5)
parallel.setData(0)
'''

#logging.console.setLevel(logging.DEBUG)#get messages about the sound lib as it loads

import time, os
import sys
import shutil
import numpy as np
import scipy.io.wavfile
from numpy import mean, sqrt, square
import math
import pandas as pd
import fnmatch


def normjoin(*arg):
    return os.path.normpath(os.path.join(*arg))



def rms(array):
    return sqrt(mean(square(array)))
def db2amp(scalar):
    return math.pow(10,scalar/20)    
    






practice = 0
test = 0
subject = str(raw_input("Subject ID: "))
blockNum = str(raw_input("Block Num: "))

numTrials = 60

initialSNR = 0
monitorSpeed = 60
startTimeStr = str(time.time())[:-3]

increaseVolume = 20

#Set paths 
rootPath = normjoin('C:/Experiments/JK306')
stimPath = normjoin('C:/TCDTIMIT/volunteersSmall')
dataOutPath = normjoin(rootPath,'dataOut',subject) 
stimOutPath = normjoin(rootPath,'stim') 

if practice:
    table = pd.read_csv(normjoin(rootPath,'StudyDesignJK306Practice_r1.csv'))
elif test:
    table = pd.read_csv(normjoin(rootPath,'StudyDesignJK306Test_r1.csv'))
else:
    table = pd.read_csv(normjoin(rootPath,'StudyDesignJK306_r1.csv'))


table = table[table['Subject']== int(subject)]
table = table[table['SubjectBlockNum']== int(blockNum)]
table = table.reset_index()
table['TargetSentence'] = ' '
table['dBSNR'] = -999
print table


timeTable = pd.read_csv(normjoin(rootPath,'audioTableTM_r1.csv'))

#timeTable['OnsetSample'] =  np.round(timeTable['OnsetSample']/float(10000000)*48000)
#timeTable['OffsetSample'] = np.round(timeTable['OffsetSample']/float(10000000)*48000)


#Find the root filenames of all of the si sentences for this talker
speechList = table['SentenceID']

vidSwitch = table['VideoCond']

    



babblePath = normjoin(rootPath,'Babble')
babbleList = ['babble'+ str(f) for f in table['BabbleFile']]
bab1File = normjoin(babblePath,'babble1.wav')
info,bab1 = scipy.io.wavfile.read(bab1File)
babbleRMS = rms(bab1)



dBSNRBabble = initialSNR
prevtalker = 'None'
talkerCnt = 0
#Start trial loop
for trial in np.arange(numTrials):
    
    
    
    
    talker = table['Talker'].iloc[trial]
    
    talkerPath = normjoin(stimPath, talker,'straightcam')
    print talkerPath
    
    if talker != prevtalker:
        talkerCnt += 1
        fname = 'sa1'
        speechFile = normjoin(talkerPath, 'sa1.wav')
        info,speech = scipy.io.wavfile.read(speechFile)
        speech = speech.astype('float32')
        # set speech to match babble1 RMS
        matchSpeech = babbleRMS/rms(speech)*speech*db2amp(increaseVolume)
        tmpSoundFile = normjoin(stimOutPath,'example' + str(talkerCnt) + '.wav')
        scipy.io.wavfile.write(tmpSoundFile, 48000, matchSpeech.astype('int16'))
    
    
    
    #Select the file to present
    fname = speechList[trial]
    
    #Shuffle and pick a random babble file with replacement
    
    bname = babbleList[trial]
    
    speechFile = normjoin(talkerPath, fname + '.wav')
    babbleFile = normjoin(babblePath, bname + '.wav')
    videoFile = normjoin(talkerPath, fname + '.avi')
    
    if table['SoundCond'][trial] == "Babble":
        dBSNR = dBSNRBabble
    elif table['SoundCond'][trial] == "Clear":
        dBSNR = 999
        
    table['dBSNR'].iloc[trial] = dBSNR        

     

    #   Find the range of speech
    tt = timeTable[(timeTable['Talker']== talker) & (timeTable['SentenceID']== fname)].reset_index()
    speechRange = tt['OnsetSample'].iloc[[1,-1]].values # FInd the range of all speech
    speechRange = np.round(speechRange)

    #Phonemic Restoration code
    #    shRange = tt[tt['Phoneme'] == 't']
    txtFile = normjoin(talkerPath, fname + '.txt')
    words = pd.read_csv(txtFile,sep = ' ',header = None,names = ['tmp0','tmp1','Words'])['Words']
    targetSentence = ' '.join(words)
    #Load in speech and babble
    info,speech = scipy.io.wavfile.read(speechFile)
    info,babble = scipy.io.wavfile.read(babbleFile)
    speech = speech.astype('float32')


    #Phonemic Restoration code
    #        if ~shRange.empty:
    #            for x in np.arange(0,len(shRange)):
    #                speech[int(shRange['Onset'].iloc[x]):int(shRange['Offset'].iloc[x])] = 0

    babble = babble[range(0,len(speech))].astype('float32')
    babbleRMS = rms(babble[range(int(speechRange[0]),int(speechRange[1]))])
    adjustedBabble = babble*db2amp(-dBSNR)
    matchSpeech = babbleRMS/rms(speech[range(int(speechRange[0]),int(speechRange[1]))])*speech
    audioOut = (matchSpeech + adjustedBabble)*db2amp(increaseVolume)

        
            
    #Export mixed speech and babble to a temporary wav file matching the trial number
    tmpSoundFile = normjoin(stimOutPath,'temp' + str(trial) + '.wav')
    scipy.io.wavfile.write(tmpSoundFile, 48000, audioOut.astype('int16'))        


    videopath= videoFile
    videopath = os.path.join(os.getcwd(),videopath)
    
    if not os.path.exists(videopath):
        raise RuntimeError("Video File could not be found:"+videopath)

    shutil.copy (videopath, normjoin(stimOutPath,'VideoFile' + str(trial) + '.avi'))


    table['TargetSentence'][trial] = targetSentence


    #Output table to file


    print 'trial ' + str(trial)
    prevtalker = talker
    
table.to_csv(normjoin(dataOutPath, 'p' + subject + '_' + blockNum + '_' + startTimeStr  +'.csv'))    
table.to_csv(normjoin(stimOutPath, 'temp.csv'))
vidSwitch.to_csv(normjoin(stimOutPath, 'tempVS.csv'),sep='\t',index=False)