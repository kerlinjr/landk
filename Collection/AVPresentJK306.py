"""Audio visual presentation of TCD-TIMIT sentences in noise EEG experiment
#Audio jitter ~+-3 ms 
#Video jitter ~+- 30 ms


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
import pyo
pyo.pa_get_input_devices()
prefs.general['audioLib'] = ['pyo']
prefs.general['audioDriver'] = ['MOTU Audio ASIO']

from psychopy import visual, sound, core, event, microphone, gui
from psychopy import logging, prefs


from psychopy import parallel
import time
port = parallel.ParallelPort(address=0xEFF8)

#Initiate the PsychPy window
win = visual.Window([1920, 1080])
sound.init(48000,buffer=512)


#logging.console.setLevel(logging.DEBUG)#get messages about the sound lib as it loads

import time, os
import sys

import numpy as np
import scipy.io.wavfile
from numpy import mean, sqrt, square
import math
import pandas as pd
import fnmatch
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
    return math.pow(10,scalar/20)    
    
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

movStimVersion = 3

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
    timeCorrection = 0.0
    talker = 's60T'
    talkerNum = '99'
    increaseVolume = 20
else:
    if practice:
        numTrials = 2
        subject = '99'
        initialSNR = 999
        monitorSpeed = 60
        startTimeStr = str(time.time())[:-3]
        timeCorrection = 0.0
        talker = 's01M'
        talkerNum = '99'
        increaseVolume = 20
    else:
        numTrials = 20
        subject = textIn[0]
        initialSNR = 0
        monitorSpeed = 60
        startTimeStr = str(time.time())[:-3]
        timeCorrection = 0.0
        talkerNum = textIn[1]
        increaseVolume = 20

#Set paths 
rootPath = normjoin('C:/Experiments/JK302')
stimPath = normjoin('C:/TCDTIMIT/volunteersSmall')
dataOutPath = normjoin(rootPath,'dataOut',subject) 
if practice:
    table = pd.read_csv(normjoin(rootPath,'StudyDesignJK302Practice_r1.csv'))
elif test:
    table = pd.read_csv(normjoin(rootPath,'StudyDesignJK302Test_r1.csv'))
else:
    table = pd.read_csv(normjoin(rootPath,'StudyDesignJK302_r1.csv'))
table = table[table['Subject']== int(subject)]
table = table[table['SubjectTalkerNum']== int(talkerNum)]
table = table.reset_index()
table['SourceSentence'] = ' '
table['TargetSentence'] = ' '
table['dBSNR'] = -999
print table
talker = table['Talker'].iloc[0]

timeTable = pd.read_csv(normjoin(rootPath,'timeTable_r1.csv'))

timeTable['Onset'] =  np.round(timeTable['Onset']/float(10000000)*48000)
timeTable['Offset'] = np.round(timeTable['Offset']/float(10000000)*48000)


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
keystext = "Please listen to and watch the talker of each sentence. Be ready to type the sentence you hear. If you you are not sure about what you heard, guess. Please attempt to report as much of the sentence you heard as possible. \n \n Press the spacebar to continue."
text = visual.TextStim(win, keystext, pos=(0, 0), units = 'pix')
text.draw()
win.flip()
core.wait(0.5)
k = event.waitKeys()


dBSNRBabble = initialSNR

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
        tt = timeTable[(timeTable['Talker']== talker[1:]) & (timeTable['SentenceID']== fname)].reset_index()
        speechRange = tt['Onset'].iloc[[1,-1]].values # FInd the range of all speech
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
        speech = speech[int(timeCorrection*48000):]
        
        #Phonemic Restoration code
#        if ~shRange.empty:
#            for x in np.arange(0,len(shRange)):
#                speech[int(shRange['Onset'].iloc[x]):int(shRange['Offset'].iloc[x])] = 0

        babble = babble[range(0,len(speech))].astype('float32')
        babbleRMS = rms(babble[range(int(speechRange[0]),int(speechRange[1]))])
        adjustedBabble = babble*db2amp(-dBSNR)
        matchSpeech = babbleRMS/rms(speech[range(int(speechRange[0]),int(speechRange[1]))])*speech
        audioOut = (matchSpeech + adjustedBabble)*db2amp(increaseVolume)

            
                
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

    globalClock = core.Clock()


    soundStart = 0
    trig2 = 1
    cnt = 1;
    #roundStart = globalClock.getTime()
    #win.flip()
    #mov.seek(.008)
    mov.draw()
    mov.seek(.008)

    portTime = 0
#    while mov.getCurrentFrameTime() <= 0:
#        time.sleep(0.001)
    while mov.status != visual.FINISHED:
        win.flip()
        roundStart = globalClock.getTime()
        port.setData(0)
        if mov.getCurrentFrameTime() > .02 and soundStart == 0:
            portTime = globalClock.getTime()
            audioSound.play()
            #time.sleep(0.008)
            port.setData(255) #sets all pins high
            soundStart = 1
            #print portTime -globalClock.getTime()

            
            
            #
        if cnt > 1:    
            if globalClock.getTime()-portTime > 1-(1/float(60)) and globalClock.getTime()-portTime < 1+(1/float(60)):
                #time.sleep(0.008)
                port.setData(255)
            elif globalClock.getTime()-portTime > 3-(1/float(60)) and globalClock.getTime()-portTime < 3+(1/float(60)):
                #time.sleep(0.008)
                port.setData(255)

        
        #time.sleep(0.003) #To get off the edge of a frame

        print mov.getCurrentFrameTime()

        if event.getKeys(keyList=['escape','q']):
            win.close()
            core.quit()  
            
        mov.draw()    
        while globalClock.getTime() - roundStart < 0.022:
            time.sleep(0.003)
        cnt +=1
    core.wait(1)
    if not test:
# No microphone procedure in this version        
#        #Start microphone sequence
#        instruct = visual.TextStim(win, "Please say what you heard. Press spacebar when you are finished:", pos=(0, 0), units = 'pix')
        text = visual.TextStim(win, "", pos=(0, -50), units = 'pix')
#
        win.flip()
#        instruct.draw()
        text.draw()
        win.flip()
#
#
#        mic.record(sec=10, block=False)
#        core.wait(0.5)
#        k = event.waitKeys()
#        mic.stop() 
#        core.wait(0.1)
        
        #Start transcription sequence
        myDlg = Dlg(title='AV Experiment', pos=(200,400), fontSize=20)
        myDlg.addField("'Please type what you heard:'", width = 80,lines =2,multiLineText=True, fontSize=20)

        textIn = [" "]
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            textIn = myDlg.data
            print(textIn)
        else:
            print('user cancelled')    

        #Record final response
        if textIn: 
            sourceSentence = textIn[0]
        else:
            sourceSentence = " "
        print sourceSentence
        print "target " + targetSentence
            

        table['SourceSentence'][trial] = sourceSentence
        table['TargetSentence'][trial] = targetSentence
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
