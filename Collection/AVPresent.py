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
from psychopy import visual, sound, core, event, microphone, gui
from psychopy import logging, prefs

import vlc
#logging.console.setLevel(logging.DEBUG)#get messages about the sound lib as it loads

import time, os
import sys

import numpy as np
import scipy.io.wavfile
from numpy import mean, sqrt, square
import math
import pandas as pd
import fnmatch
#Add landkit path (needed for spell checking, sentence alignement and word scoring)
sys.path.append(r'C:\Users\jrkerlin\Documents\GitHub\landk\Analysis')
import landkit
reload(landkit)

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



subject = textIn[0]
numTrials = 36
initialSNR = int(textIn[1])
monitorSpeed = 60
startTimeStr = str(time.time())[:-3]

table = pd.DataFrame(columns = {'Subject','Speaker','dBSNR','TrialNum','FileName','VideoFile','VideoCond','Babble','TargetSentence','SourceSentence','SpellCorrSource','SentenceWordScore'}, index = np.arange(numTrials))
#Set paths 
stimPath = r'C:/TCDTIMIT/volunteersSmall/'
dataOutPath = r'C:/TCDTIMIT/dataOut/' + subject + r'/' + startTimeStr + r'/'
speaker = textIn[2]
speakerPath = stimPath + speaker + r'/straightcam/'
#Find the root filenames of all of the si sentences for this speaker
speechList = [f[:-4] for f in os.listdir(speakerPath) if fnmatch.fnmatch(f, 'si*.mp4')]

#Check that you have the expected number of mp4 files
if len(speechList) != numTrials:
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
win = visual.Window([1920, 1080])


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
core.wait(exampleSentence.duration)

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
    txtFile = speakerPath + fname + '.txt'
    table['FileName'][trial] = fname
    table['VideoFile'][trial] = videoFile
    table['Babble'][trial] = bname
    table['dBSNR'][trial] = dBSNR
    #load in text
    words = pd.read_csv(txtFile,sep = ' ',header = None,names = ['tmp0','tmp1','Words'])['Words']
    targetSentence = ' '.join(words)

    #Load in speech and babble
    info,speech = scipy.io.wavfile.read(speechFile)
    info,babble = scipy.io.wavfile.read(babbleFile)
    speech = speech.astype('float32')
    babble = babble[range(0,len(speech))].astype('float32')
    babbleRMS = rms(babble)
    matchSpeech = babbleRMS/rms(speech)*speech
    adjustedBabble = babble*db2amp(-dBSNR)
    audioOut = matchSpeech + adjustedBabble
    #Export mixed speech and babble to a temporary wav file
    scipy.io.wavfile.write(tmpSoundFile, 48000, audioOut.astype('int16'))        
    
    if prefs.general['audioLib'][0] == 'pyo':
        #if pyo is the first lib in the list of preferred libs then we could use small buffer
        #pygame sound is very bad with a small buffer though
        sound.init(48000,buffer=128)

    videopath= videoFile
    videopath = os.path.join(os.getcwd(),videopath)
    if not os.path.exists(videopath):
        raise RuntimeError("Video File could not be found:"+videopath)
        

    
    # Create your movie stim.
    mov = visual.MovieStim2(win, videopath,
                           size=720,
                           # pos specifies the /center/ of the movie stim location
                           pos=[0, 150],
                           flipVert=False,
                           flipHoriz=False,
                           loop=False,
                           noAudio = False)
                           
    #Replace movie audio with desired speech audio
    try:
        mov._audio_stream = mov._vlc_instance.media_new(tmpSoundFile)
    except NameError:
        raise ImportError('NameError: %s vs LibVLC %s' % (vlc.__version__,vlc.libvlc_get_version()))
    mov._audio_stream_player = mov._vlc_instance.media_player_new()
    mov._audio_stream_player.set_media(mov._audio_stream)
    mov._audio_stream_event_manager = mov._audio_stream_player.event_manager()
    #mov._audio_stream_event_manager.event_attach(vlc.EventType.MediaPlayerTimeChanged, mov._audio_time_callback, mov._audio_stream_player)
    #mov._audio_stream_event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, mov._audio_end_callback)
    
    keystext = "PRESS 'escape' to Quit.\n"
    text = visual.TextStim(win, keystext, pos=(0, -250), units = 'pix')
    # Start the movie stim by preparing it to play
    
    
    #Only draw more than 1 frame if this is a video "OFF" trial    
    shouldflip = mov.play()
    firstFrame = 1
    movStart  = core.getTime()
    while mov.status != visual.FINISHED and core.getTime()-movStart < mov.duration + .030:
        # Only flip when a new frame should be displayed. Can significantly reduce
        # CPU usage. This only makes sense if the movie is the only /dynamic/ stim
        # displayed.
        if shouldflip:
            # Movie has already been drawn , so just draw text stim and flip
            #if vidSwitch is not normal, only present the first frame (
            if vidSwitch[trial] == 'Normal' or core.getTime()-movStart < 2/monitorSpeed:
                text.draw()     
                win.flip()
                firstFrame = 0
            else:
                time.sleep(0.001)
        else:
            # Give the OS a break if a flip is not needed
            time.sleep(0.001)
        # Drawn movie stim again. Updating of movie stim frames as necessary
        # is handled internally.
                #Only draw more than 1 frame if this is a video On trial    
        shouldflip = mov.draw()
        # Check for action keys.....
        for key in event.getKeys():
            if key in ['escape']:
                win.close()
                core.quit()

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
    
    #Start transcription sequence
    instruct = visual.TextStim(win, "Please type what you heard:", pos=(0, 0), units = 'pix')
    text = visual.TextStim(win, "", pos=(0, -50), units = 'pix')
    
    win.flip()
    instruct.draw()
    text.draw()
    win.flip()
    
    #Prompt and collect typed response
    textIn = [" "]
    from guinam import Dlg
    myDlg = Dlg(title='AV Experiment', pos=(200,400), fontSize=20)
    myDlg.addField("'Please type what you heard:'", width = 80,lines =2,multiLineText=True, fontSize=20)


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
    sc.SpellCorrect()
    sc.ScoreWords()
    wscore = sc.wscore
    print wscore
    table['SpellCorrSource'][trial] = sc.source[0]
    table['SentenceWordScore'][trial] = wscore[0]
    
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