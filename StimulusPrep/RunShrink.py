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
       
    #sndArray = videoclip.audio.to_soundarray(fps=48000)
    #rand = np.random.rand(len(sndArray))
    #sndArray[:,0] = sndArray[:,0]*rand
    #sndArray[:,1] = sndArray[:,1]*rand
    #snd = moviepy.audio.AudioClip.AudioArrayClip(sndArray,48000)
    #video = videoclip.set_audio(snd)
    
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
folders = os.listdir('C:/TCDTIMIT/volunteersFull/')
folders = folders
centerpoints = pd.read_csv('C:/TCDTIMIT/facecenterpoints/FaceCenterPointsBridge.csv')

        
for cnt,folder in enumerate(folders):
    centerpointx = centerpoints['centerpointx'][cnt]
    centerpointy = centerpoints['centerpointy'][cnt]
    fullPath = 'C:/TCDTIMIT/volunteersFull/' + folder + '/straightcam/'
    smallPath = 'C:/TCDTIMIT/volunteersSmall/' + folder + '/straightcam/'
    if not os.path.exists(smallPath):
        os.makedirs(smallPath)
    filenames = [f[:-4] for f in os.listdir(fullPath) if fnmatch.fnmatch(f, '*.mp4')]
    for fname in filenames:
        mp4FileIn = fullPath + fname + '.mp4'
        mp4FileOut = smallPath + fname + '.mp4'
        wavFileIn = fullPath + fname + '.wav'
        wavFileOut = smallPath + fname + '.wav'
        txtFileIn = fullPath + fname.upper() + '.txt'
        txtFileOut = smallPath + fname.upper() + '.txt'
    
        ShrinkVideo(mp4FileIn,mp4FileOut,centerpointx,centerpointy)
        CopyFile(wavFileIn,wavFileOut)
        CopyFile(txtFileIn,txtFileOut)



 
