
import cv2
import numpy as np
import argparse
import glob
import scipy.stats as stats
import os
import matplotlib.pyplot as plt

def binarize(i, bkg=None, thresh=35):
    if bkg!= None:
        diff = bkg - i
        diff[diff <=0] = 0
        diff = (diff**2)/bkg
    else:
        diff = i
    r, binary = cv2.threshold(diff.astype(np.uint8), thresh, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3,3),np.uint8)
    binary = cv2.erode(binary, kernel, iterations=1)
    return binary
    
def countFish(binaryArray):
    contourImage = binaryArray.copy()
    contours, hierarchy1 = cv2.findContours(contourImage.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    bodyCount = 0
    for cnt in contours:
        if cv2.contourArea(cnt) <=1000:
            if cv2.contourArea(cnt) >= 5:
                bodyCount +=1
    return bodyCount

def markCentroids(img, bkg):
    binaryArray = binarize(img[:,:,0], bkg)
    contourImage = binaryArray.copy()
    contours, hierarchy1 = cv2.findContours(contourImage.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    bodyCount = []
    for cnt in contours:
        if cv2.contourArea(cnt) <=1000:
            if cv2.contourArea(cnt) >= 5:
                bodyCount.append(cnt)
    for c in bodyCount:
        M = cv2.moments(c)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        cv2.circle(img, (cx, cy), 3, (0,255,0), -1)
    cv2.putText(img,   str(len(bodyCount)) + ' objects', (1800, 2000), cv2.FONT_HERSHEY_SIMPLEX,1, (255,255,255), 3)  
    return img


def sho(image):
    plt.imshow(image)
    plt.colorbar()
    plt.show()
    return

def getMaxCount(vid, bkg=None):
    """takes cv2 video instance, returns max number of fish"""
    framecount = int(vid.get(7))
    skipFrames = int(np.round(framecount/25)) #FIXME return to 85
    frameList = range(1,framecount, skipFrames)
    maxCount = 0
    maxFrame = 0
    for frame in frameList:
        vid.set(1, frame)
        ret, _img = vid.read()    
        if ret == True:
            i = _img[:,:,0]
            count = countFish(binarize(i, bkg, 35))
            if count > maxCount:
                maxCount = count
                maxFrame = frame
        else:
            vid.release()
            break  
    
    vid.set(1, maxFrame)
    ret, _img = vid.read()
    vid.set(1,1)
    return maxCount ,   binarize(_img[:,:,0], bkg, 35), maxFrame

def createBackgroundImage(vid):
    """takes cv2 video instance, returns image with modal pixel values"""
    framecount = int(vid.get(7))
    skipFrames = int(np.round(framecount/10)) #FIXME return to 50
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


def count_from_vid(videofile):

    savedir, filename = videofile.rsplit('/', 1)
    if os.path.exists(savedir + '/bkg.npy'):
        bkg = np.load(savedir + '/bkg.npy')
    else:
        bkg = createBackgroundImage(cv2.VideoCapture(videofile))
        np.save(savedir + '/bkg.npy', bkg)
    vid = cv2.VideoCapture(videofile)
    maxFish, maxImage, maxFrameNum =  getMaxCount(vid, bkg)
    vid.set(1, maxFrameNum)
    di = markCentroids(vid.read()[1], bkg)
    cv2.imwrite(savedir + '/count_' + str(maxFish) + '_' + filename.split('.')[0] + '.png', di)    
    return maxFish
    
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--v', type=str, required=True,
                        help='path to video')
    parser.add_argument('--bkg', type=str, required=False, default=None,
                        help='path to background')
    args = parser.parse_args()
    
    
    if args.bkg == None:
        if os.path.exists(args.v.rsplit('/',1)[0] + '/bkg.npy'):
            bkg = np.load(args.v.rsplit('/',1)[0] + '/bkg.npy')
        elif args.v.split('.')[-1] != 'mp4':
            filelist = []
            for x in glob.glob(args.v + '/*.mp4'):
                filelist.append(x)
            bkg=createBackgroundImage(cv2.VideoCapture(filelist[-1]))
            np.save(args.v.rsplit('/',1)[0] + '/bkg.npy', bkg)
        else:
            bkg=createBackgroundImage(cv2.VideoCapture(args.v))
            np.save(args.v.rsplit('/',1)[0] + '/bkg.npy', bkg)
    elif args.bkg=='36':
        bkg = np.load('/home/dbath/fishMAD/bkg_36.npy')
    elif args.bkg.split('.')[-1] == 'npy':
        bkg = np.load(args.bkg)
    else:
        bkg = cv2.imread(args.bkg)[:,:,0]
    
    if args.v.split('.')[-1] != 'mp4':
        maxList = []
        for f in glob.glob(args.v + '/*.mp4'):
            maxList.append(getMaxCount(cv2.VideoCapture(f), bkg)[0])
        maxFish = max(maxList)
        _, maxImage, maxFrameNum = getMaxCount(cv2.VideoCapture(f), bkg)
    else:
        savedir, filename = args.v.rsplit('/', 1)
        vid = cv2.VideoCapture(args.v)
        maxFish, maxImage, maxFrameNum =  getMaxCount(vid, bkg)
        vid.set(1, maxFrameNum)
        di = markCentroids(vid.read()[1])
        
        cv2.imwrite(savedir + '/count_' + str(maxFish) + '_' + filename.split('.')[0] + '.png', di)
        
    
    print "\n\nDetected " + str(maxFish) + " objects.\n\n\n" 
    
