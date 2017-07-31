import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import pandas as pd
import argparse
import os
import imgstore
from bisect import bisect_left



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

def find_lt(a, x):
    'Find rightmost value less than x'
    i = bisect_left(a, x)
    if i:
        return a[i-1]
    raise ValueError


def getEvent(ts, events, when='before'):
    """
    pass timestamp and table of event times from visual stimulus
    returns annotations: usually:  timeOfEvent, nDots, Coherence, Velocity, Direction
    "when": before - get most recent event preceding timestamp (default)
            after  - get first event occuring after timestamp
    """
    try:
        if when == 'before':
    
    
    except:
        note = events.ix[0]
    
    
    return note

if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--v', type=str, required=True,
                        help='path to video directory')
    parser.add_argument('--log', type=str, required=True,
                        help='path to stimlog')
    parser.add_argument('--startTime', type=int, required=False, default=0,
                        help='number of seconds since vidstart to start annotation')
    parser.add_argument('--endTime', type=int, required=False, default=None,
                        help='number of seconds since vidstart to end annotation')
    args = parser.parse_args()

    DIRECTORY = args.v
    if DIRECTORY[-1] != '/':
        DIRECTORY += '/'

    store = imgstore.new_for_filename(args.v + 'metadata.yaml' )
    FPS = 30
    videoSize =store.image_shape


    stimData = pd.read_table(args.log, sep='\t', header=None, names=['Timestamp','nDots','C','vel','dir']).dropna()
    out = cv2.VideoWriter(DIRECTORY + 'annotated.mp4', cv2.cv.FOURCC('a','v','c','1'), FPS, videoSize)
    for n in range(0,store.frame_count):
        
        img, (frame_number, frame_timestamp) = store.get_next_image()

        if n % 9 == 0:
            status = getEvent(frame_timestamp, stimData)
            image = annotate_image(_img)
        
    
