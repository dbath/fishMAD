import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import pandas as pd
import argparse
import os
import imgstore



def createBackgroundImage(vid):
    """takes cv2 video instance, returns image with modal pixel values"""
    framecount = int(vid.get(7))
    skipFrames = int(np.round(framecount/50))
    frameList = range(1,framecount, skipFrames)
    for frame in frameList:
        vid.set(1, frame)
        ret, _img = vid.read()    
        if ret == True:
            i = _img[:,:,0]
            if frame == 1:
                img_array = i
            else:
                img_array = np.dstack((img_array, i))
        else:
            vid.release()
            break  
    mode = stats.mode(img_array, axis=2)[0][:,:,0]
    vid.set(1,1)
    return mode


def binarize(i, bkg=None, thresh=50):
    if bkg!=None:
        binary = (i- bkg)/bkg
        binary[binary>=-0.4] = 255
        binary[binary<-0.4] = 0
    else:
        r, binary = cv2.threshold(i, thresh, 255, cv2.THRESH_BINARY)
    
    return binary

def countFish(binaryArray):
    contourImage = binaryArray.copy()
    contours, hierarchy1 = cv2.findContours(contourImage.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    bodyCount = 0
    for cnt in contours:
        if cv2.contourArea(cnt) <=10000:
            if cv2.contourArea(cnt) >= 20:
                bodyCount +=1
    return bodyCount


def getMaxCount(vid, bkg=None):
    """takes cv2 video instance, returns max number of fish"""
    framecount = int(vid.get(7))
    skipFrames = int(np.round(framecount/50))
    frameList = range(1,framecount, skipFrames)
    maxCount = 0
    for frame in frameList:
        vid.set(1, frame)
        ret, _img = vid.read()    
        if ret == True:
            i = _img[:,:,0]
            count = countFish(binarize(i, bkg, 50))
            if count > maxCount:
                maxCount = count
        else:
            vid.release()
            break  
    vid.set(1,1)
    return maxCount   



def imsho(_i):
    plt.imshow(_i)
    plt.colorbar()
    plt.show()
    return()

def annotateFrame(ts, events):
    """
    pass timestamp and table of event times from visual stimulus
    """
    
    return note

if __name__ == "__main__":
    
    store = imgstore.new_for_filename('/media/recnodes/recnode_jolle2/36_sunbleaks_x0128_100sstim_20170726_083552/metadata.yaml' )

    stimData = pd.read_table(s, sep='\t', header=None, names=['Timestamp','nDots','C','vel','dir']).dropna()

    for n in range(0,store.frame_count):
        img, (frame_number, frame_timestamp) = store.get_next_image()
        
    
