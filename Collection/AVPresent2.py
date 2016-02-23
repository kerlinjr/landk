"""Audio visual presentation of TCD-TIMIT sentences in noise


PsychoPy movie presentation dependencies:
Movie2 does require:
~~~~~~~~~~~~~~~~~~~~~

1. Python OpenCV package (so openCV libs and the cv2 python interface).
    *. For Windows, a binary installer is available at http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv
    *. For Linux, it is available via whatever package manager you use.
    *. For OSX, ..... ?
2. VLC application. Just install the standard VLC (32bit) for your OS. http://www.videolan.org/vlc/index.html
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

logging.console.setLevel(logging.DEBUG)#get messages about the sound lib as it loads

import time, os
import sys

import numpy as np
import scipy.io.wavfile
from numpy import mean, sqrt, square
import math
import pandas as pd
import fnmatch
from guinam import Dlg
#Add landkit path (needed for spell checking, sentence alignement and word scoring)
landkPath = os.path.normpath(os.getcwd() + os.sep + os.pardir+r'\Analysis')
sys.path.append(landkPath)
import landkit
reload(landkit)
import enchant

def rms(array):
    return sqrt(mean(square(array)))
def db2amp(scalar):
    return math.pow(10,scalar/20)    
    
textIn = [" "]
myDlg = gui.Dlg(title='AV Experiment')
myDlg.addField("'Subject: '")
myDlg.addField("'initialSNR: '")
myDlg.addField("'Speaker: '")


myDlg.show()  # show dialog and wait for OK or Cancel
if myDlg.OK:  # then the user pressed OK
    textIn = myDlg.data
    print(textIn)
else:
    print('user cancelled')    



test = 0

if test:
    numTrials = 6
    subject = 'tmp'
    initialSNR = 40
    monitorSpeed = 60
    startTimeStr = str(time.time())[:-3]
    timeCorrection = 0.070
    speaker = 's60T'
else:
    numTrials = 36
    subject = textIn[0]
    initialSNR = int(textIn[1])
    monitorSpeed = 60
    startTimeStr = str(time.time())[:-3]
    timeCorrection = 0.070
    speaker = textIn[2]

table = pd.DataFrame(columns = {'Subject','Speaker','dBSNR','TrialNum','FileName','VideoFile','VideoCond','Babble','TargetSentence','SourceSentence','SpellCorrSource','SentenceWordScore'}, index = np.arange(numTrials))
#Set paths 
stimPath = r'C:/TCDTIMIT/volunteersSmall/'
dataOutPath = r'C:/TCDTIMIT/dataOut/' + subject + r'/' + startTimeStr + r'/'

speakerPath = stimPath + speaker + r'/straightcam/'
#Find the root filenames of all of the si sentences for this speaker
if test:
    speechList = [f[:-4] for f in os.listdir(speakerPath) if fnmatch.fnmatch(f, 'Test*.mp4')]
else:
    speechList = [f[:-4] for f in os.listdir(speakerPath) if fnmatch.fnmatch(f, 'si*.mp4')]

#Check that you have the expected number of mp4 files
if len(speechList) != numTrials:
    print speechList
    print 'Exiting...: Unexpected number of qualified *.mp4 files'
    core.quit()
    
#Randomize the order of the speechList
np.random.shuffle(speechList)    
tmpSoundFile = r'C:/TCDTIMIT/Temp/temp.wav'
babblePath = r'C:/TCDTIMIT/Babble/'
babbleList = [f[:-4] for f in os.listdir(babblePath) if fnmatch.fnmatch(f, 'babble*.wav')]
bab0File = babblePath + r'babble0.wav'
info,bab0 = scipy.io.wavfile.read(bab0File)
babbleRMS = rms(bab0)

#Randomize video condition
vidSwitch = (["Normal"]*int(numTrials/2))
vidSwitch.extend(["Static"]*int(numTrials/2)) 
vidSwitch = np.array(vidSwitch)
np.random.shuffle(vidSwitch)

# Set up microphone, must be 16000 or 8000 Hz for speech recognition
microphone.switchOn(sampleRate=16000)
mic = microphone.AdvAudioCapture(name='mic', saveDir=dataOutPath, stereo=False)

#Initiate the PsychPy window
win = visual.Window([1000, 1000])
#sound.init(48000,buffer=500)

if not test:
    #Present an example of the speaker without noise. No response taken.
    keystext = "The first sentence you will hear is an example sentence from the target speaker you will be listening for. Please listen to the example sentence. You will not need to make any response.Press spacebar when ready. "
    text = visual.TextStim(win, keystext, pos=(0, 0), units = 'pix')
    text.draw()
    win.flip()
    core.wait(0.5)
    k = event.waitKeys()



    #Present an example of the speaker without noise. No response taken.
    keystext = "Please listen to the Speaker Example Sentence"
    text = visual.TextStim(win, keystext, pos=(0, 0), units = 'pix')
    text.draw()
    win.flip()
    core.wait(0.5)
    fname = 'sa1'
    speechFile = speakerPath + 'sa1.wav'
    info,speech = scipy.io.wavfile.read(speechFile)
    speech = speech.astype('float32')
    # set speech to match babble0 RMS
    matchSpeech = babbleRMS/rms(speech)*speech
    scipy.io.wavfile.write(tmpSoundFile, 48000, matchSpeech.astype('int16'))
    exampleSentence = sound.Sound(tmpSoundFile)
    exampleSentence.play()
    core.wait(exampleSentence.getDuration())

#Present an example of the speaker without noise. No response taken.
keystext = "Please listen to and watch the speaker of each sentence. Be ready to type the sentence you hear. If you you are not sure about what you heard, guess. Please attempt to report as much of the sentence you heard as possible. \n \n Press the spacebar to continue."
text = visual.TextStim(win, keystext, pos=(0, 0), units = 'pix')
text.draw()
win.flip()
core.wait(0.5)
k = event.waitKeys()


dBSNR = initialSNR

#Start trial loop
for trial in np.arange(numTrials):
    reload(enchant)
    table['Subject'][trial] = subject
    table['Speaker'][trial] = speaker
    table['TrialNum'][trial] = trial
    table['VideoCond'][trial] = vidSwitch[trial]
    
    #Select the file to present
    fname = speechList[trial]
    
    #Shuffle and pick a random babble file with replacement
    np.random.shuffle(babbleList)
    bname = babbleList[0]
    
    speechFile = speakerPath + fname + '.wav'
    babbleFile = babblePath + bname + '.wav'
    videoFile = speakerPath + fname + '.mp4'

    table['FileName'][trial] = fname
    table['VideoFile'][trial] = videoFile
    table['Babble'][trial] = bname
    table['dBSNR'][trial] = dBSNR
    
    #load in text
    if not test:
        txtFile = speakerPath + fname + '.txt'
        words = pd.read_csv(txtFile,sep = ' ',header = None,names = ['tmp0','tmp1','Words'])['Words']
        targetSentence = ' '.join(words)
        #Load in speech and babble
        info,speech = scipy.io.wavfile.read(speechFile)
        info,babble = scipy.io.wavfile.read(babbleFile)
        speech = speech.astype('float32')
        speech = speech[int(timeCorrection*48000):]
        babble = babble[range(0,len(speech))].astype('float32')
        babbleRMS = rms(babble)
        matchSpeech = babbleRMS/rms(speech)*speech
        adjustedBabble = babble*db2amp(-dBSNR)
        audioOut = matchSpeech + adjustedBabble
        #Export mixed speech and babble to a temporary wav file
        scipy.io.wavfile.write(tmpSoundFile, 48000, audioOut.astype('int16'))        
    else:
        info,speech = scipy.io.wavfile.read(speakerPath + 'TestVideo.wav')
        speech = speech[int(timeCorrection*48000):]
        scipy.io.wavfile.write(tmpSoundFile, 48000, speech.astype('int16'))

    videopath= videoFile
    videopath = os.path.join(os.getcwd(),videopath)
    if not os.path.exists(videopath):
        raise RuntimeError("Video File could not be found:"+videopath)
        

    
    # Create your movie stim.
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
    print soundDur
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
            if vidSwitch[trial] == 'Normal' or test:
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
        #Start microphone sequence
        instruct = visual.TextStim(win, "Please say what you heard. Press spacebar when you are finished:", pos=(0, 0), units = 'pix')
        text = visual.TextStim(win, "", pos=(0, -50), units = 'pix')

        win.flip()
        instruct.draw()
        text.draw()
        win.flip()


        mic.record(sec=10, block=False)
        core.wait(0.5)
        k = event.waitKeys()
        mic.stop() 
        core.wait(0.1)
        
        #Start transcription sequence
        instruct = visual.TextStim(win, "Please type what you heard:", pos=(0, 0), units = 'pix')
        text = visual.TextStim(win, "", pos=(0, -50), units = 'pix')
        
        win.flip()
        instruct.draw()
        text.draw()
        win.flip()
        

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
        #Just the spell correction and word -level scoring
        sc = landkit.SentCompare([targetSentence],[sourceSentence],False)
        
        sc.SpellCorrectNorvig() #enchant crashes this script at testing computer for unknown reason!!! 
        
        sc.ScoreWords()
        
        wscore = sc.wscore
        print wscore
        table['SpellCorrSource'][trial] = sc.source[0]
        table['SentenceWordScore'][trial] = wscore[0]
        del sc
        #Adapt dbSNR on every trial
        if wscore > 50:
            dBSNR += -3
        elif wscore == 50:
            dBSNR += 0
        elif wscore < 50:
            dBSNR += 3    

        #Output table to file
        table.to_csv(dataOutPath+ subject + startTimeStr  +'.csv')


        # Report word score to participants
        keystext = "Trial score: " + str(int(round(wscore)))
        text = visual.TextStim(win, keystext, pos=(0, 0), units = 'pix')
        text.draw()
        win.flip()
        core.wait(0.5)
        


print table
core.quit()
