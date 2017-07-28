
import cv2
import numpy as np
import argparse
import glob

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
    
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--v', type=str, required=True,
                        help='path to video')
    parser.add_argument('--bkg', type=str, required=False, default=None,
                        help='path to background')
    args = parser.parse_args()
    
    if args.bkg=='36':
        bkg = np.load('/home/dbath/fishMAD/bkg_36.npy')
    elif args.bkg.split('.')[-1] == 'npy':
        bkg = np.load(args.bkg)
    elif args.bkg == None:
        bkg=None
    else:
        bkg = cv2.imread(args.bkg)[:,:,0]
    
    if args.v.split(',')[-1] != 'mp4':
        maxList = []
        for f in glob.glob(args.v + '/*.mp4'):
            maxList.append(getMaxCount(cv2.VideoCapture(f), bkg))
        maxFish = max(maxList)
    else:
        vid = cv2.VideoCapture(args.v)
        maxFish =  getMaxCount(vid, bkg)
    
    print "\n\nDetected " + str(maxFish) + " objects.\n\n\n" 
    
