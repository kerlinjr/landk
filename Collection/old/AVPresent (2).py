"""
Demo using the new (beta) MovieStim2 to play a video file. Path of video
needs to updated to point to a video you have. MovieStim2 does /not/ require
avbin to be installed. But...

Movie2 does require:
~~~~~~~~~~~~~~~~~~~~~

1. Python OpenCV package (so openCV libs and the cv2 python interface).
    *. For Windows, a binary installer is available at http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv
    *. For Linux, it is available via whatever package manager you use.
    *. For OSX, ..... ?
2. VLC application. Just install the standard VLC (32bit) for your OS. http://www.videolan.org/vlc/index.html
"""
from __future__ import division
from psychopy import visual, sound, core, event
import time, os
import sys
import vlc
from psychopy import logging, prefs
logging.console.setLevel(logging.DEBUG)#get messages about the sound lib as it loads

# Sound Code (based on SoundStimuli demo)
import numpy as np
import scipy.io.wavfile
import time
from numpy import mean, sqrt, square
import math
import pandas as pd

def rms(array):
    return sqrt(mean(square(array)))
def db2amp(scalar):
    return math.pow(10,scalar/20)    

table = pd.DataFrame(columns = {'Subject','TrialNum','Speaker','VideoFile','Babble','dBSNR','TargetSentence','SourceSentence','WordScore'})
#Set paths 
stimPath = r'C:/TCDTIMIT/volunteersSmall/'
speaker = 's01M'
speakerPath = stimPath + speaker + r'/straightcam/'
fname = 'sa1'
tmpSoundFile = r'C:/TCDTIMIT/Temp/temp.wav'
babblePath = r'C:/TCDTIMIT/Babble/'
bname = 'babble0'
dBSNR = 20

speechFile = speakerPath + fname + '.wav'
babbleFile = babblePath + bname + '.wav'
videoFile = speakerPath + fname + '.mp4'
t1 = time.time()
info,speech = scipy.io.wavfile.read(speechFile)
info,babble = scipy.io.wavfile.read(babbleFile)
speech = speech.astype('float32')
babble = babble[range(0,len(speech))].astype('float32')
babbleRMS = rms(babble)
matchSpeech = babbleRMS/rms(speech)*speech
adjustedBabble = babble*db2amp(-dBSNR)
audioOut = matchSpeech + adjustedBabble
scipy.io.wavfile.write(tmpSoundFile, 48000, audioOut.astype('int16'))
t2 = time.time()
print "time"+" "+str(t2-t1)


if prefs.general['audioLib'][0] == 'pyo':
    #if pyo is the first lib in the list of preferred libs then we could use small buffer
    #pygame sound is very bad with a small buffer though
    sound.init(48000,buffer=128)
print 'Using %s(with %s) for sounds' %(sound.audioLib, sound.audioDriver)

videopath= videoFile
videopath = os.path.join(os.getcwd(),videopath)
if not os.path.exists(videopath):
    raise RuntimeError("Video File could not be found:"+videopath)
    
win = visual.Window([1024, 768])

# Create your movie stim.
mov = visual.MovieStim2(win, videopath,
                       size=640,
                       # pos specifies the /center/ of the movie stim location
                       pos=[0, 100],
                       flipVert=False,
                       flipHoriz=False,
                       loop=False,
                       noAudio = False)

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
shouldflip = mov.play()
while mov.status != visual.FINISHED:
    # Only flip when a new frame should be displayed. Can significantly reduce
    # CPU usage. This only makes sense if the movie is the only /dynamic/ stim
    # displayed.
    if shouldflip:
        # Movie has already been drawn , so just draw text stim and flip
        text.draw()
        win.flip()
    else:
        # Give the OS a break if a flip is not needed
        time.sleep(0.001)
    # Drawn movie stim again. Updating of movie stim frames as necessary
    # is handled internally.
    shouldflip = mov.draw()

    # Check for action keys.....
    for key in event.getKeys():
        if key in ['escape']:
            win.close()
            core.quit()

# -*- coding: utf-8 -*-
chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',"'"]
text = visual.TextStim(win, " ", pos=(0, -250), units = 'pix')
win.flip()
text.draw()
win.flip()

# Loop until return is pressed
endTrial = False

while not endTrial:
    # Wait for response...
    response = event.waitKeys()
    if response:
        # If backspace, delete last character
        if response[0] == 'backspace':
            text.setText(text.text[:-1])

        # If return, end trial
        elif response[0] == 'return':
            endTrial = True

        # Insert space
        elif response[0] == 'space':
            text.setText(text.text + ' ')

        # Else if a letter, append to text:
        elif response[0] in chars:
            text.setText(text.text + response[0])

    # Display updated text
    text.draw()
    win.flip()
    

# Print final response
print text.text



core.quit()