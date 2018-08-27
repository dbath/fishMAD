 """
 This script calculates the homography values for a group of 4 cameras. 
 
 Input: a directory with undistorted videos containing busy, non-repetitive 
        images with sufficient overlapping regions.
        
 Output: three sets of homography values: top row, bottom row, and top-to-bottom
         a stitched image
 """
 
 
 
 import numpy as np
 import imutils
 import cv2
 from homography import Stitcher
 import yaml


 def showFeatures(listy, LOCATION):
     plt.imshow(imgs[LOCATION])
     xs = []
     ys = []
     for i in listy[LOCATION]:
        xs.append(i[0])
        ys.append(i[1])
     plt.scatter(xs, ys, color='r')
     plt.show()
     return


def getImages(directory):
    imgs = []
    for fn in glob.glob(directory + '/*undistorted.mp4'):
        vid = cv2.VideoCapture(fn)
        ret, img = vid.read()
        imgs.append(img)
    return imgs

def getIt(directory):
    imgs = []
    kpsList = []
    featList = []
    for fn in glob.glob(directory + '/*undistorted.mp4'):
        vid = cv2.VideoCapture(fn)
        ret, img = vid.read()
        imgs.append(img)
        (k,f) = detectAndDescribe(img)
        kpsList.append(k)
        featList.append(f)
    return imgs, kpsList, featList

  
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=True, help='path to videos')
    parser.add_argument('--handle', type=str, required=False, default='',
                                    help='unique catchall for videos to be stitched. timestamp works well')
    parser.add_argument('--saveas', type=str, required=False, default='notAssigned', help='output filename')
    args = parser.parse_args()
    
    SEARCH_FILES = '/media/recnodes/recnode_2mfish/stitch10000_20180503_160717/undistorted/stitch*'
    #SEARCH_FILES = slashdir(args.dir) + '*' +  args.handle + '*undistorted.mp4'
    
    #Camera orientations before renovation:
    [tl, bl, tr, br] = ['21990445',
                        '21990447',
                        '21990449',
                        '21990443']

    #Camera orientations after renovation (August 2018):
    """ #Current settings as of 180827
    [tl, bl, tr, br] = ['21990447',
                        '21990449',
                        '21990443',
                        '21990445']

    """
    
    for x in glob.glob(SEARCH_FILES):
        ID = x.split('_')[-2].split('.')[-1]
        print ID
        if br in ID:
            BOTTOM_RIGHT = cv2.VideoCapture(x)
        elif tl in ID:
            TOP_LEFT = cv2.VideoCapture(x)
        elif bl in ID:
            BOTTOM_LEFT = cv2.VideoCapture(x)
        elif tr in ID:
            TOP_RIGHT = cv2.VideoCapture(x)
            
    VIDEOS = [TOP_LEFT, BOTTOM_LEFT, TOP_RIGHT, BOTTOM_RIGHT]
    
    #CALCULATE HOMOGRAPHY
    imgs = []
    for v in VIDEOS:               
        v.set(1,7)
        ret, i = v.read()
        if ret:
            imgs.append(i)
        else:
            break
    (top, top_vis), Mtop = stitcher.getHomography([imgs[0],imgs[2]], showMatches=True)
    (bot, bot_vis) Mbot = stitcher.stitch([imgs[1],imgs[3]], showMatches=True) 
    (result, vis) Mtotal = stitcher.stitch([top,bot], showMatches=True) 
    
    if not None in [Mtop, Mbot, Mtotal]:
        H = {'topRow':Mtop[1], 'bottomRow': Mbot[1], 'final':Mtotal[1]}
        
def stitchRL(    
    
            
        
        
