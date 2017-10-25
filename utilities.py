
import cv2
import numpy as np
import scipy.stats as stats



def createBackgroundImage(DIRECTORY, method='mode'):
    """
    takes directory of mp4s, 
    returns image with modal pixel values from the first video
    """
    if DIRECTORY[-1] != '/':
        DIRECTORY += '/'
        
    vid = cv2.VideoCapture(DIRECTORY + '000000.mp4')
    framecount = int(vid.get(7))
    skipFrames = int(np.round(framecount/200))
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
    if method == 'mode':
        bkgImg = stats.mode(img_array, axis=2)[0][:,:,0]
    elif method == 'mean':
        bkgImg = img_array.mean(axis=2)
    vid.set(1,1)
    return bkgImg
