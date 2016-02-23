# -*- coding: utf-8 -*-
"""Creates cliped and reduced sized mp4 files, and copies text and wavs from TIMIT to get a ~20X reduction in disk space
Bug: Only works with 64-bit python?
Created on Wed Feb 03 17:17:29 2016

@author: jrkerlin
"""
import moviepy
import numpy 
from moviepy.editor import *
    
import win32file
import os
import fnmatch
import pandas as pd



import scipy.ndimage.measurements

def ShrinkVideo(inputfile,outputfile,centerPointx,centerPointy):
    #Dont overwrite files, skip if file exists
    if os.path.isfile (outputfile): 
        return
    #Import, crop the video, resize the video     
    videoclip = (VideoFileClip(inputfile)
                .fx( vfx.crop, x1=centerpointx-440-1, y1=centerpointy-440-1, x2=centerpointx+440, y2=centerpointy+440))    
    rs = videoclip.resize(height=720)

    fps = 48000   
#    rand = np.random.rand(len(sndArray))
    #Erase Sound
    sndArray = numpy.zeros([fps*5, 2])
    #Add 5ms clicks at 1000 and 3000 ms
    sndArray[fps*1:int(fps*1.005),0] = 1
    sndArray[fps*1:int(fps*1.005),1] = 1
    sndArray[fps*3:int(fps*3.005),0] = 1
    sndArray[fps*3:int(fps*3.005),1] = 1
    snd = moviepy.audio.AudioClip.AudioArrayClip(sndArray,fps)
    rs = rs.set_audio(snd)
    # Report back if writing file failed
    try:
        rs.write_videofile(outputfile)
    except IOError:
        print "Failed to make " + outputfile

        

def CopyFile(inputfile,outputfile):
    if os.path.isfile (outputfile): 
        return
    print inputfile, "=>", outputfile
    
    win32file.CopyFile (inputfile, outputfile, 1)
    
    if os.path.isfile (outputfile): print "Success"

#Start script

centerpoints = pd.read_csv('C:/TCDTIMIT/facecenterpoints/FaceCenterPointsBridge.csv')


cnt = 1
centerpointx = centerpoints['centerpointx'][cnt]
centerpointy = centerpoints['centerpointy'][cnt]
fullPath = 'C:/TCDTIMIT/Test/'
smallPath = 'C:/TCDTIMIT/Test/Small/'

fname ='TestVideo'
mp4FileIn = fullPath + fname + '.mp4'
mp4FileOut = smallPath + fname + '.mp4'
ShrinkVideo(mp4FileIn,mp4FileOut,centerpointx,centerpointy)




 
