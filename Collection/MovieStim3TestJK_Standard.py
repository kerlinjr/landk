
from psychopy import prefs
#pyo.pa_get_input_devices()
#prefs.general['audioLib'] = ['pygame']
#prefs.general['audioDriver'] = ['SPDIF (RME HDSP 9652)']

from psychopy import visual, core, event,sound,logging
logging.console.setLevel(logging.DEBUG)#get messages about the sound lib as it loads

win = visual.Window([1000,1000])
#sound.init(48000,buffer=500)

globalClock = core.Clock()

#mov._audioStream = testSound
for trl in range(0,4):
    mov = visual.MovieStim3(win, r'C:\TCDTIMIT\volunteersSmall\s60T\straightcam\TestVideo.mp4',
                       flipVert=False, flipHoriz=False, loop=False,noAudio=True)
    testSound = sound.Sound(r'C:\TCDTIMIT\volunteersSmall\s60T\straightcam\TestVideo.wav',sampleRate=48000)  
    #core.wait(.2)
    print('orig movie size=%s' %(mov.size))
    print('duration=%.2fs' %(mov.duration))
    movStart = 1
    while mov.status != visual.FINISHED:
        mov.draw()
        win.flip()
        if movStart:
            testSound.play()
            movStart = 0
        if event.getKeys(keyList=['escape','q']):
            win.close()
            core.quit()
    core.wait(1)

core.quit()

"""Different systems have different sets of codecs.
avbin (which PsychoPy uses to load movies) seems not to load compressed audio on all systems.
To create a movie that will play on all systems I would recommend using the format:
    video: H.264 compressed,
    audio: Linear PCM
"""
