"""Audio visual presentation of TCD-TIMIT linear noise level, yes-no response to target word
#AUDIOVISUAL Synchrony TIMING CURRENTLY NOT PERFECT (+- 15ms, centered near 0)
#ONLY for behavioural use, not EEG
# 

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

from psychopy import prefs
#pyo.pa_get_input_devices()
#prefs.general['audioLib'] = ['pygame']
#prefs.general['audioDriver'] = ['SPDIF (RME HDSP 9652)'] #kills none spdif microphone


from psychopy import visual, sound, core, event, microphone, gui
from psychopy import logging, prefs
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
import random
import numpy as np
import scipy.io.wavfile
from numpy import mean, sqrt, square
import math
import pandas as pd
import fnmatch
import re

from guinam import Dlg

def normjoin(*arg):
    return os.path.normpath(os.path.join(*arg))
#No l andKit loading in this version
#Add landkit path (needed for spell checking, sentence alignement and word scoring)
#landkPath = os.path.normpath(os.getcwd() + os.sep + os.pardir+r'\Analysis')
#sys.path.append(landkPath)
#import landkit
#reload(landkit)
#NWORDS=landkit.norvigTrain()

#import enchant



def rms(array):
    return sqrt(mean(square(array)))  
def db2amp(scalar):
    return np.power(10,scalar/20)   
def amp2db(scalar):
    return np.log10(scalar)*20    
    
textIn = [" "]
myDlg = gui.Dlg(title='AV Experiment')
myDlg.addField("'Subject: '")
myDlg.addField("'TalkerNum: '")
myDlg.addField("'If practice type y here: '")


myDlg.show()  # show dialog and wait for OK or Cancel
if myDlg.OK:  # then the user pressed OK
    textIn = myDlg.data
    print(textIn)
else:
    print('user cancelled')    

movStimVersion = 2

test = 0
if textIn[2] == 'y':
    practice = 1
    test = 0
elif textIn[2] == 't':
    practice = 0
    test = 1
else:
    practice = 0
    test = 0
    
if test:
    numTrials = 6
    subject = '99'
    initialSNR = 999
    monitorSpeed = 60
    startTimeStr = str(time.time())[:-3]
    timeCorrection = 0.070
    talker = 's60T'
    talkerNum = '99'
    increaseVolume = 20
else:
    if practice:
        numTrials = 8
        subject = '99'
        initialSNR = 999
        monitorSpeed = 60
        startTimeStr = str(time.time())[:-3]
        timeCorrection = 0.070
        talker = 's01M'
        talkerNum = '99'
        increaseVolume = 20
    else:
        numTrials = 20
        subject = textIn[0]
        initialSNR = 0
        monitorSpeed = 60
        startTimeStr = str(time.time())[:-3]
        timeCorrection = 0.070
        talkerNum = textIn[1]
        increaseVolume = 20

#Set paths 
rootPath = normjoin('C:/Experiments/JK310')
stimPath = normjoin('C:/TCDTIMIT/volunteersSmall')
dataOutPath = normjoin(rootPath,'dataOut',subject) 
if practice:
    table = pd.read_csv(normjoin(rootPath,'StudyDesignJK310Practice_r1.csv'))
elif test:
    table = pd.read_csv(normjoin(rootPath,'StudyDesignJK310Test_r1.csv'))
else:
    table = pd.read_csv(normjoin(rootPath,'StudyDesignJK310_r1.csv'))    
    table = table[table['Subject']== int(subject)]
    table = table[table['SubjectTalkerNum']== int(talkerNum)]

corpusList = pd.DataFrame.from_csv("C:\Experiments\JK310\Dictionaries\TCDTIMIT\Dict.txt").transpose()
corpusTrim = []
for x in corpusList.index:
    pattern = '[a-z]'
    corpusTrim.append(''.join(re.findall(pattern, str(x))))






    
    
#if np.mod(int(subject),2) == 1:
#    if np.mod(int(talkerNum),2) == 1:
#        wordLoc = ['First3']*int(len(table))    
#    elif np.mod(int(talkerNum),2) == 0:
#        wordLoc = ['Last3']*int(len(table))
#elif np.mod(int(subject),2) == 0:
#    if np.mod(int(talkerNum),2) == 1:
#        wordLoc = ['Last3']*int(len(table))    
#    elif np.mod(int(talkerNum),2) == 0:
#        wordLoc = ['First3']*int(len(table))
    

#table['WordLoc'] = wordLoc
table['WordIdxList'] = [-1]*len(table)
table = table.reset_index()
table['SourceSentence'] = ' '
table['TargetSentence'] = ' '
table['FullSentence'] = ' '
table['Response'] = ' '
table['dBSNR'] = -999
print table
talker = table['Talker'].iloc[0]

timeTable = pd.read_csv(normjoin(rootPath,'audioTableTM.csv'))

timeTable['OnsetSample'] =  np.round(timeTable['OnsetSample'])
timeTable['OffsetSample'] = np.round(timeTable['OffsetSample'])


talkerPath = normjoin(stimPath, talker,'straightcam')
print talkerPath
#Find the root filenames of all of the si sentences for this talker
if test:
    speechList = [f[:-4] for f in os.listdir(talkerPath) if fnmatch.fnmatch(f, 'Test*.mp4')]
else:
    speechList = table['SentenceID']

vidSwitch = table['VideoCond']

#Check that you have the expected number of mp4 files
if not practice == 1:
    if not test == 1:
        if len(speechList) != numTrials:
            print speechList
            print 'Exiting...: Unexpected number of qualified *.mp4 files'
            core.quit()
    

tmpSoundFile = normjoin(rootPath,'temp.wav')
babblePath = normjoin(rootPath,'Babble')
babbleList = ['babble'+ str(f) for f in table['BabbleFile']]
bab1File = normjoin(babblePath,'babble1.wav')
info,bab1 = scipy.io.wavfile.read(bab1File)
babbleRMS = rms(bab1)

# Set up microphone, must be 16000 or 8000 Hz for speech recognition
microphone.switchOn(sampleRate=16000)
mic = microphone.AdvAudioCapture(name='mic', saveDir=dataOutPath, stereo=False)

#Initiate the PsychPy window
win = visual.Window([1920, 1080])
#sound.init(48000,buffer=500)

if not test:
    #Present an example of the talker without noise. No response taken.
    keystext = "Please listen to the example sentence.Press spacebar when ready. "
    text = visual.TextStim(win, keystext, pos=(0, 0), units = 'pix')
    text.draw()
    win.flip()
    core.wait(0.5)
    k = event.waitKeys()



    #Present an example of the talker without noise. No response taken.
    keystext = "Please listen to the Talker Example Sentence"
    text = visual.TextStim(win, keystext, pos=(0, 0), units = 'pix')
    text.draw()
    win.flip()
    core.wait(0.5)
    fname = 'sa1'
    speechFile = normjoin(talkerPath, 'sa1.wav')
    info,speech = scipy.io.wavfile.read(speechFile)
    speech = speech.astype('float32')
    # set speech to match babble1 RMS
    matchSpeech = babbleRMS/rms(speech)*speech*db2amp(increaseVolume)
    scipy.io.wavfile.write(tmpSoundFile, 48000, matchSpeech.astype('int16'))
    exampleSentence = sound.Sound(tmpSoundFile)
    exampleSentence.play()
    core.wait(exampleSentence.getDuration())

#Present an example of the talker without noise. No response taken.
keystext = "Press 1 if you hear the target word. Press 2 if you do not hear the target word. Press spacebar to continue "
text = visual.TextStim(win, keystext, pos=(0, 0), units = 'pix')
text.draw()
win.flip()
core.wait(0.5)
k = event.waitKeys()


dBSNRBabble = initialSNR
wordIdxList = []
#Start trial loop
for trial in np.arange(numTrials):

    #Select the file to present
    fname = speechList[trial]
    
    #Shuffle and pick a random babble file with replacement
    
    bname = babbleList[trial]
    
    speechFile = normjoin(talkerPath, fname + '.wav')
    babbleFile = normjoin(babblePath, bname + '.wav')
    videoFile = normjoin(talkerPath, fname + '.mp4')
    
    if table['SoundCond'][trial] == "Babble":
        dBSNR = dBSNRBabble
    elif table['SoundCond'][trial] == "Clear":
        dBSNR = 999
        
    table['dBSNR'].iloc[trial] = dBSNR        


     
     
    #load in text
    if not test:
        #   Find the range of speech
        tt = timeTable[(timeTable['Talker']== talker[0:]) & (timeTable['SentenceID']== fname)].reset_index()
        speechRange = np.round(np.array([tt['OnsetSample'].iloc[[0]].values[0], tt['OffsetSample'].iloc[[-1]].values[0]])) # FInd the range of all speech
        
        #Phonemic Restoration code
        numWords = tt['WordIndex'].max()+1
        from random import randint


        #wordsToLose = list(set(range(0,numWords)) - set([wordIdx]))
#        shRange = tt[tt['WordIndex'].isin(wordKeep)]
        shRange = tt
        
        txtFile = normjoin(talkerPath, fname + '.txt')
        words = pd.read_csv(txtFile,sep = ' ',header = None,names = ['tmp0','tmp1','Words'])['Words']
        #targetSentence = ' '.join(words[wordKeep])
        fullSentence = ' '.join(words)
        if table['TargetCond'][trial] == 'Present':
            probePosition = table['ProbePosition'][trial]
            targetSentence = words[probePosition]
        else:
            randWord = random.choice(corpusTrim)
            while randWord in words:
                randWord = random.choice(corpusTrim)
            targetSentence = randWord    
            
        #Load in speech and babble
        info,speech = scipy.io.wavfile.read(speechFile)
        info,babble = scipy.io.wavfile.read(babbleFile)
        speech = speech.astype('float32')
        polyC = np.polyfit((shRange['OnsetSample']+shRange['OffsetSample'])/2,amp2db(shRange['SpeechRMS']),1)
        x = np.arange(0,len(speech))
        spPoly = np.polyval(polyC,x)
        spNorm = spPoly-mean(spPoly);
        spAdjust = db2amp(-spNorm);
        speech[range(int(speechRange[0]),int(speechRange[1]))] = speech[range(int(speechRange[0]),int(speechRange[1]))]*spAdjust[range(int(speechRange[0]),int(speechRange[1]))];
        babble = babble[range(0,len(speech))].astype('float32')
        babbleRMS = rms(babble[range(int(speechRange[0]),int(speechRange[1]))])
        adjustedBabble = babble*db2amp(-dBSNR)
        matchSpeech = babbleRMS/rms(speech[range(int(speechRange[0]),int(speechRange[1]))])*speech
        audioOut = (matchSpeech + adjustedBabble)*db2amp(increaseVolume)    
        
#        speechTmp = audioOut
#        audioOut = audioOut*0
#        #Phonemic Restoration code
#        if ~shRange.empty:
#            audioOut[int(shRange['OnsetSample'].iloc[0]):int(shRange['OffsetSample'].iloc[len(shRange)-1])] = speechTmp[int(shRange['OnsetSample'].iloc[0]):int(shRange['OffsetSample'].iloc[len(shRange)-1])] 
#        
#        audioOut = audioOut[int(timeCorrection*48000):]        




            
                
        #Export mixed speech and babble to a temporary wav file
        scipy.io.wavfile.write(tmpSoundFile, 48000, audioOut.astype('int16'))        
    else:
        info,speech = scipy.io.wavfile.read(normjoin(talkerPath, 'TestVideo.wav'))
        speech = speech[int(timeCorrection*48000):]
        scipy.io.wavfile.write(tmpSoundFile, 48000, speech.astype('int16'))

    videopath= videoFile
    videopath = os.path.join(os.getcwd(),videopath)
    if not os.path.exists(videopath):
        raise RuntimeError("Video File could not be found:"+videopath)
    
    #Declare probe word for if Before condition
    if table['ProbeBeforeAfter'][trial] == 'Before':
        keystext = targetSentence
        text = visual.TextStim(win, keystext, pos=(0, 0), units = 'pix')
        text.draw()
        win.flip()
        event.clearEvents(eventType=None)
        core.wait(1)
    
    # Create your movie stim.
    if movStimVersion == 2:    
        mov = visual.MovieStim2(win, videopath,
                               size=720,
                               # pos specifies the /center/ of the movie stim location
                               pos=[0, 150],
                               flipVert=False,
                               flipHoriz=False,
                               loop=False,
                               noAudio = True)
        audioSound = sound.Sound(tmpSoundFile,sampleRate=48000)
        soundDur = audioSound.getDuration()
    else:
        mov = visual.MovieStim3(win, videopath,
                               size=720,
                               # pos specifies the /center/ of the movie stim location
                               pos=[0, 150],
                               flipVert=False,
                               flipHoriz=False,
                               loop=False,
                               noAudio = True)
        audioSound = sound.Sound(tmpSoundFile,sampleRate=48000)
        soundDur = audioSound.getDuration()
    
    keystext = "PRESS 'escape' to Quit.\n"
    text = visual.TextStim(win, keystext, pos=(0, -250), units = 'pix')
    
    
    #Only draw more than 1 frame if this is a video "OFF" trial    
    firstFrame = 1
    
    movStart = core.getTime()
    while core.getTime()-movStart < soundDur+ .1: #mov.status != visual.FINISHED:
        if firstFrame ==1:
            mov.draw()
            text.draw()     
            win.flip()
            audioSound.play()
            movStart  = core.getTime()
            firstFrame = 0
        else:
            if vidSwitch[trial] == 'AV' or test:
                mov.draw()
                text.draw()     
                win.flip()
        # Check for action keys.....
        for key in event.getKeys():
            if key in ['escape']:
                win.close()
                core.quit()
        time.sleep(0.005)
        
    if not test:
# No microphone procedure in this version        
#        #Start microphone sequence
#        instruct = visual.TextStim(win, "Please say what you heard. Press spacebar when you are finished:", pos=(0, 0), units = 'pix
#
#
#        mic.record(sec=10, block=False)
#        core.wait(0.3)
#        k = event.waitKeys()
#        mic.stop() 
#        core.wait(0.1)
        
        #Collect probe response and delare target for After condition
        if table['ProbeBeforeAfter'][trial] == 'After':
            keystext = targetSentence
        else:
            keystext = '?'
        text = visual.TextStim(win, keystext, pos=(0, 0), units = 'pix')
        text.draw()
        win.flip()
        event.clearEvents(eventType=None)
        response  = event.waitKeys()
        print response




        #Record final response
        if table['TargetCond'][trial] == 'Present':
            if response[0] in ['num_1']:
                sourceSentence = targetSentence
                table['Response'][trial] = 'Hit'
            else:
                sourceSentence = " "
                table['Response'][trial] = 'Miss'
        else:
            if response[0] in ['num_1']:
                sourceSentence = targetSentence
                table['Response'][trial] = 'False Alarm'
            else:
                sourceSentence = " "
                table['Response'][trial] = 'Correct Rejection'
        print targetSentence
        print table['Response'][trial]
            

        table['SourceSentence'][trial] = sourceSentence
        table['TargetSentence'][trial] = targetSentence
        table['FullSentence'][trial] = fullSentence 
#        No adaptation in this version
#        #Just the spell correction and word -level scoring
#        sc = landkit.SentCompare([targetSentence],[sourceSentence],False)
#        
#        #sc.SpellCorrect() #enchant crashes this script at testing computer for unknown reason!!! 
#        sc.SpellCorrectNorvig() 
#        
#        sc.ScoreWords()
#         
#        wscore = sc.wscore
#        print wscore
#        table['SpellCorrSource'][trial] = sc.source[0]
#        table['SentenceWordScore'][trial] = wscore[0]
#        del sc
#        #Adapt dbSNR on every noise trial
#        if table['BabbleCond'][trial] == "On":
#            if wscore > 50:
#                dBSNRBabble += -2
#            elif wscore == 50:
#                dBSNRBabble += 0
#            elif wscore < 50:
#                dBSNRBabble += 2    

        #Output table to file
        table.to_csv(normjoin(dataOutPath, 'p' + subject + '_' + talkerNum + '_' + startTimeStr  +'.csv'))

#        # Report word score to participants
#        keystext = "Trial score: " + str(int(round(wscore)))
#        text = visual.TextStim(win, keystext, pos=(0, 0), units = 'pix')
# Sentence feedback this version
#    text = visual.TextStim(win, "Actual: "+ targetSentence, pos=(0, 0), units = 'pix')
#    text2 = visual.TextStim(win, "Response: "+ sourceSentence, pos=(0, -100), units = 'pix')
#    text.draw()
#    win.flip()
#    core.wait(1.5)
        


print table
core.quit()
