
import cv2
import numpy as np
import scipy.stats as stats
import os
import pandas as pd
import glob
import math

XPOS = 'X#centroid (cm)'
YPOS = 'Y#centroid (cm)'
XVEL = 'VX#centroid (cm/s)' 
YVEL = 'VY#centroid (cm/s)'

def createBackgroundImage(DIRECTORY, method='mode'):
    """
    takes directory of mp4s, 
    returns image with modal pixel values from the first video
    """
    if DIRECTORY[-1] != '/':
        DIRECTORY += '/'
        
    firstframe=True
    for vidnum in ['000000.mp4','000010.mp4']:  #LAZY DANNO FIXME    
        vid = cv2.VideoCapture(DIRECTORY + vidnum)
        framecount = int(vid.get(7))
        skipFrames = 1#int(np.round(framecount/100))
        frameList = range(1,framecount, skipFrames)
        for frame in frameList:
            vid.set(1, frame)
            ret, _img = vid.read()    
            if ret == True:
                i = _img[:,:,0]
                if firstframe:
                    img_array = i
                    firstframe = False
                else:
                    img_array = np.dstack((img_array, i))
            else:
                vid.release()
                break  
    if method == 'mode':
        bkgImg = stats.mode(img_array, axis=2)[0][:,:,0]
    elif method == 'mean':
        bkgImg = img_array.mean(axis=2)
    vid.set(1,1)
    return bkgImg

def slashdir(string):
    if string[-1] != '/':
        return string + '/'
    else:
        return string
    
def getFrameByFrameData(DIRECTORY, RESUME=True):

    if DIRECTORY[-1] != '/':
        DIRECTORY = DIRECTORY + '/'
        
    if os.path.exists(DIRECTORY + 'frameByFrameData.pickle') and RESUME:
        df = pd.read_pickle(DIRECTORY + 'frameByFrameData.pickle')
    else:
        df = pd.DataFrame()
    i = 0
    for fn in glob.glob(DIRECTORY + 'fishdata/*.csv'):
        ID = fn.split('fish')[-1].split('.')[0]
        if (len(df) >0):
            if not (ID in df['trackid'].values):
                f = pd.read_csv(fn)
                f['trackid'] = ID
                df = pd.concat([df, f])
        else:
            f = pd.read_csv(fn)
            f['trackid'] = ID
            df = pd.concat([df, f])

        if i%500 == 0:
            print "processed track number :", i
            df.to_pickle(DIRECTORY + 'frameByFrameData.pickle')
        i +=1
    print df
    df['frame'] = df['frame'].astype(int)
    df.replace(to_replace=np.inf, value=np.nan, inplace=True)
    df.to_pickle(DIRECTORY + 'frameByFrameData.pickle')
    open(DIRECTORY + 'frameByFrame_complete','a').close()
    return df
    
def angle_from_vertical(point1, point2):
    """
    RETURNS A VALUE IN DEGREES BETWEEN 0 AND 360, WHERE 0 AND 360 ARE NORTH ORIENTATION.
    """
    x = point1[0] - point2[0]
    y = point1[1] - point2[1]
    return 180.0 + math.atan2(x,y)*180.0/np.pi

def angle_from_heading(velA,pointA, pointB): 
    velTheta = angle_from_vertical((0,0),velA)
    pointTheta = angle_from_vertical(pointA, pointB)
    angle = pointTheta - velTheta
    if angle >= 180:
        angle -= 360.0
    elif angle <= -180:
        angle += 360.0
    return angle

def getFramelessValues(myDict):
    myArray = []
    for x in myDict:
        for y in myDict[x]:
            myArray.append(y)
    myArray = np.array(myArray)
    return myArray

