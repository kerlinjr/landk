# This results in a "on-time" AV presentation on our setup +- about 15 ms (missed flip?)
from psychopy import prefs
import pyo
pyo.pa_get_input_devices()
prefs.general['audioLib'] = ['pyo']
#prefs.general['audioDriver'] = ['MOTU Analog 1-2 (MOTU Audio Wave for 64 bit)']
#prefs.general['audioDriver'] = ['ASIO Hammerfall DSP']
prefs.general['audioDriver'] = ['MOTU Audio ASIO']

from psychopy import visual, core, event,sound,logging
logging.console.setLevel(logging.DEBUG)#get messages about the sound lib as it loads


from psychopy import parallel
import time
port = parallel.ParallelPort(address=0xEFF8)



win = visual.Window([1920,1080])
sound.init(48000,buffer=500)

globalClock = core.Clock()

#mov._audioStream = testSound
for trl in range(0,20):
   # mov = visual.MovieStim3(win, r'C:\TCDTIMIT\volunteersSmall\s60T\straightcam\TestVideo.mp4',flipVert=False, size=720, flipHoriz=False, loop=False,noAudio=True)
    testSound = sound.Sound(r'C:\TCDTIMIT\volunteersSmall\s60T\straightcam\TestVideo.wav',sampleRate=48000) 
    mov = visual.MovieStim3(win, r'C:\TCDTIMIT\volunteersSmall\s60T\straightcam\TestVideo.mp4',flipVert=False,size = 720,flipHoriz=False,loop=False,noAudio = True)
    #mov = visual.MovieStim(win, r'C:\TCDTIMIT\volunteersSmall\s60T\straightcam\TestVideo.mp4')
    core.wait(.5)
    print('orig movie size=%s' %(mov.size))
    print('duration=%.2fs' %(mov.duration))
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
            
            testSound.play()
            portTime = globalClock.getTime()
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

core.quit()

"""Different systems have different sets of codecs.
avbin (which PsychoPy uses to load movies) seems not to load compressed audio on all systems.
To create a movie that will play on all systems I would recommend using the format:
    video: H.264 compressed,
    audio: Linear PCM
"""
