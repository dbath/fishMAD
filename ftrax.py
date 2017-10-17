import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import pandas as pd
import argparse
import os
import imgstore
from bisect import bisect_left, bisect_right




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

def find_gt(a, x):
    'Find leftmost value greater than x'
    i = bisect_right(a, x)
    if i != len(a):
        return a[i]
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
            x = (events['Timestamp'] < ts*1000).idxmin() - 1
            #x = bisect_left(events['Timestamp'].values, ts*1000) -1
        elif when == 'after':
            x = (events['Timestamp'] < ts*1000).idxmin()
            #x = bisect_right(events['Timestamp'].values, ts*1000)
        
        note = events.ix[x]
    except:
        note = events.ix[0] * 0
    return note

def annotateImage(_img, _status):
    if (_status.vel * _status.dir) > 0:
        return _img - cw
    elif (_status.vel * _status.dir) < 0:
        return _img - ccw
    else:
        return _img

if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--v', type=str, required=True,
                        help='path to video directory')
    parser.add_argument('--log', type=str, required=True,
                        help='path to stimlog')
    parser.add_argument('--output', type=str, required=True,
                        help='path to save directory')
                        
    parser.add_argument('--startTime', type=int, required=False, default=0,
                        help='number of seconds since vidstart to start annotation')
    parser.add_argument('--endTime', type=int, required=False, default=None,
                        help='number of seconds since vidstart to end annotation')
    parser.add_argument('--centreTime', type=int, required=False, default=None,
                        help='timestamp (milliseconds) to center annotation')
    parser.add_argument('--duration', type=int, required=False, default=None,
                        help='if centreTime, number of seconds movie length')
            
    args = parser.parse_args()

    DIRECTORY = args.v
    if DIRECTORY[-1] != '/':
        DIRECTORY += '/'
    
    LOG = args.log

    stimData = pd.read_table(LOG, sep='\t', header=None, names=['Timestamp','nDots','C','vel','dir']).fillna(0)
    stimData['frame_time'] = stimData['Timestamp']/1000.0
    
    store = imgstore.new_for_filename(DIRECTORY + 'metadata.yaml' )
    FPS = 30
    videoSize =store.image_shape
    
    frameDF = pd.DataFrame(store.get_frame_metadata())
    merged = frameDF.merge(stimData, how='outer', on='frame_time')
    merged = merged.sort('frame_time').reset_index(drop=True)

    merged['frame_number'] = merged['frame_number'].fillna(0)
    
    merged[['nDots','C','vel','dir']] = merged[['nDots','C','vel','dir']].fillna(method='ffill', axis=0)

    merged['date_and_time'] = pd.to_datetime(merged['frame_time'], unit='s')

    
    
    
    if args.centreTime == None:
        if args.startTime == 0:
            firstLogEntry = getEvent(frameDF.ix[0].frame_time, stimData, 'after')
            firstFrame = frameDF.ix[frameDF[frameDF.frame_time >= firstLogEntry.Timestamp/1000].idxmin().frame_time].frame_number
        else:
            startTS = frameDF.ix[0].frame_time + args.startTime
            firstFrame = frameDF.ix[frameDF[frameDF.frame_time >= startTS].idxmin().frame_time].frame_number
        
            print "firstFrame: ", firstFrame, startTS
        if args.endTime == None:
            nFrames = int(store.frame_max - firstFrame - 2)
        else:
            endTS = frameDF.ix[0].frame_time + args.endTime
            lastFrame = frameDF.ix[frameDF[frameDF.frame_time <= endTS].idxmax().frame_time].frame_number
            nFrames = int(lastFrame - firstFrame)
    else:
        centreTS = args.centreTime
        startTS = (centreTS - args.duration*500)/1000.0
        endTS = (centreTS + args.duration*500)/1000.0
        firstFrame = frameDF.ix[frameDF[frameDF.frame_time >= startTS].idxmin().frame_time].frame_number
        lastFrame = frameDF.ix[frameDF[frameDF.frame_time <= endTS].idxmax().frame_time].frame_number
        nFrames = int(lastFrame - firstFrame)

        print "firstFrame: ", firstFrame, startTS
        print "lastFrame: ", lastFrame, endTS         
    #out = cv2.VideoWriter(DIRECTORY + 'annotated.mp4', cv2.cv.FOURCC('a','v','c','1'), FPS, videoSize)
    
    out = imgstore.new_for_format('mjpeg', mode='w', basedir=args.output,imgshape=store.image_shape, imgdtype=store.get_image(store.frame_min)[0].dtype, chunksize=1000)
    
    ccw = cv2.imread('/home/dbath/fishMAD/counterclockwise.png' )[:,:,1]
    cw = cv2.imread('/home/dbath/fishMAD/clockwise.png' )[:,:,1]
    
    img, (frame_number, frame_timestamp) = store.get_image(firstFrame)
    
    
    for n in range(0,nFrames,9):
        
        img, (frame_number, frame_timestamp) = store.get_image(store.frame_min + n)

        status = getEvent(frame_timestamp, stimData)
        image = annotateImage(img, status)
        cv2.putText(image, '3x speed D.Bath 2017.07.27' ,(1400,2000), cv2.FONT_HERSHEY_SIMPLEX, 1.4, 255, 2)
        out.add_image(image, n, frame_timestamp)
        
        if (n % 1000 == 0) & (n != 0):
            print 'Processed ', str(n), ' frames.', str(frame_timestamp), status.Timestamp, str(status.vel*status.dir)
            
    out.close()
    
