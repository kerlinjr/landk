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
import scipy


import scipy.ndimage.measurements



def BlurVideo(inputfile,outputfile):
    #Dont overwrite files, skip if file exists
    if os.path.isfile (outputfile): 
        return
    #Import, crop the video, resize the video     
    cv2.CV_AA = cv2.LINE_AA   
    videoclip = (VideoFileClip(inputfile)
                .fx( vfx.headblur, fx=lambda x : x*0+360, fy=lambda x : x*0+520, r_zone=150, r_blur=100))    
    #videoclip = moviepy.video.fx.all.headblur(clip, 360, 360, 200, r_blur=1)
    #shutil.copy (filename1, normjoin(stimOutPath,'VideoFile'))
    videoclip.write_videofile(outputfile)
       
    #sndArray = videoclip.audio.to_soundarray(fps=48000)
    #rand = np.random.rand(len(sndArray))
    #sndArray[:,0] = sndArray[:,0]*rand
    #sndArray[:,1] = sndArray[:,1]*rand
    #snd = moviepy.audio.AudioClip.AudioArrayClip(sndArray,48000)
    #video = videoclip.set_audio(snd)
    
    # Report back if writing file failed
    try:
        rs.write_videofile(outputfile)
    except:
        pass
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

        
for cnt,folder in enumerate(folders):
    fullPath = 'C:/TCDTIMIT/volunteersSmall/' + folder + '/straightcam/'
    smallPath = 'C:/TCDTIMIT/volunteersBlur/' + folder + '/straightcam/'
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
    
        BlurVideo(mp4FileIn,mp4FileOut)
        CopyFile(wavFileIn,wavFileOut)
        CopyFile(txtFileIn,txtFileOut)



 
