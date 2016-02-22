from psychopy import visual, core, event

win = visual.Window([1000,1000])
mov = visual.MovieStim3(win, r'C:\TCDTIMIT\volunteersSmall\s60T\straightcam\TestVideo.mp4',
                       flipVert=False, flipHoriz=False, loop=False)
print('orig movie size=%s' %(mov.size))
print('duration=%.2fs' %(mov.duration))
globalClock = core.Clock()

while mov.status != visual.FINISHED:
    mov.draw()
    win.flip()
    if event.getKeys(keyList=['escape','q']):
        win.close()
        core.quit()

core.quit()

"""Different systems have different sets of codecs.
avbin (which PsychoPy uses to load movies) seems not to load compressed audio on all systems.
To create a movie that will play on all systems I would recommend using the format:
    video: H.264 compressed,
    audio: Linear PCM
"""
