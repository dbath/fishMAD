 import numpy as np
 import imutils
 import cv2


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
 
 class Stitcher:
    def __init__(self, trainer=False):
    
        if trainer == True:
            self.H1, self.H2, self.H3 = self.calculateHomography()
        else:
            self.H1, self.H2, self.H3 = self.loadHomography()
        return
    
    def calculateHomography(self):
    
        (kpsTL, featuresTL) = self.detectAndDescribe(TL)
        (kpsTR, featuresTR) = self.detectAndDescribe(TR)
        (kpsBL, featuresBL) = self.detectAndDescribe(BL)
        (kpsBR, featuresBR) = self.detectAndDescribe(BR)
                
        M1 = self.matchKeyPoints(kpsTL, kpsTR, 
                                featuresTL, featuresTR, 
                                ratio, reprojThresh)
        (matches, H, status) = M1
        
        TopImage = stitchTwo(TL, TR, kpsTL, kpsTR, featuresTL, featuresTR, ratio, reprojThresh, 'horizontal')
                        
        M2 = self.matchKeyPoints(kpsBL, kpsBR, 
                                featuresBL, featuresBR, 
                                ratio, reprojThresh)
        
        if M is None:
            return None

        
        (matches, H, status) = M
        
                    
        return H1, H2, H3
            
    def loadHomography(self):
        pass
        return H1, H2, H3

    
    def stitch(self, listOfImages, ratio=1.0, reprojThresh=4.0):

        (TL, TR, BL, BR) = listOfImages        

        
        #First match &stitch the top images
        TOP = self.stitchTwo(TL, TR,
                             kpsTL, kpsTR, 
                             featuresTL, featuresTR, 
                             ratio, reprojThresh, 'horizontal') #1 for horizontal, 0 for vertical
    
    
    def stitchTwo(self, imageA, imageB, kpsA, kpsB, featuresA, featuresB,ratio, reprojThresh, axis):    
        
        if axis=='horizontal':
            (ax1, ax2) = (1,0)
        elif axis == 'vertical':
            (ax1, ax2) = (0,1)
            

        result = cv2.warpPerspective(imageA, H,
                        (imageA.shape[ax1] + imageB.shape[ax1], imageA.shape[ax2]))
            
        result[0:imageB.shape[0], 0:imageB.shape[1]] = imageB
        """
        # check to see if the keypoint matches should be visualized
        if showMatches:
            vis = self.drawMatches(imageA, imageB, kpsA, kpsB, matches,
                status)

            # return a tuple of the stitched image and the
            # visualization
            return (result, vis)
        """
        # return the stitched image
        return result  
        
        
        
    def detectAndDescribe(self, image):
        # convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # check to see if we are using OpenCV 3.X
        if self.isv3:
            # detect and extract features from the image
            descriptor = cv2.xfeatures2d.SIFT_create()
            (kps, features) = descriptor.detectAndCompute(image, None)

        # otherwise, we are using OpenCV 2.4.X
        else:
            # detect keypoints in the image
            detector = cv2.FeatureDetector_create("SIFT")
            kps = detector.detect(gray)

            # extract features from the image
            extractor = cv2.DescriptorExtractor_create("SIFT")
            (kps, features) = extractor.compute(gray, kps)

        # convert the keypoints from KeyPoint objects to NumPy
        # arrays
        kps = np.float32([kp.pt for kp in kps])

        # return a tuple of keypoints and features
        return (kps, features)

    def matchKeypoints(self, kpsA, kpsB, featuresA, featuresB,
        ratio, reprojThresh):
        # compute the raw matches and initialize the list of actual
        # matches
        matcher = cv2.DescriptorMatcher_create("BruteForce")
        rawMatches = matcher.knnMatch(featuresA, featuresB, 2)
        matches = []

        # loop over the raw matches
        for m in rawMatches:
            # ensure the distance is within a certain ratio of each
            # other (i.e. Lowe's ratio test)
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                matches.append((m[0].trainIdx, m[0].queryIdx))

        # computing a homography requires at least 4 matches
        if len(matches) > 4:
            # construct the two sets of points
            ptsA = np.float32([kpsA[i] for (_, i) in matches])
            ptsB = np.float32([kpsB[i] for (i, _) in matches])

            # compute the homography between the two sets of points
            (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC,
                reprojThresh)

            # return the matches along with the homograpy matrix
            # and status of each matched point
            return (matches, H, status)

        # otherwise, no homograpy could be computed
        return None

    def drawMatches(self, imageA, imageB, kpsA, kpsB, matches, status):
        # initialize the output visualization image
        (hA, wA) = imageA.shape[:2]
        (hB, wB) = imageB.shape[:2]
        vis = np.zeros((max(hA, hB), wA + wB, 3), dtype="uint8")
        vis[0:hA, 0:wA] = imageA
        vis[0:hB, wA:] = imageB

        # loop over the matches
        for ((trainIdx, queryIdx), s) in zip(matches, status):
            # only process the match if the keypoint was successfully
            # matched
            if s == 1:
                # draw the match
                ptA = (int(kpsA[queryIdx][0]), int(kpsA[queryIdx][1]))
                ptB = (int(kpsB[trainIdx][0]) + wA, int(kpsB[trainIdx][1]))
                cv2.line(vis, ptA, ptB, (0, 255, 0), 1)

        # return the visualization
        return vis      
  
  
  
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=True, help='path to videos')
    parser.add_argument('--saveas', type=str, required=False, default='notAssigned', help='output filename')
    args = parser.parse_args()

    VIDEO_FILES = []

    for x in glob.glob(slashdir(args.dir) + '*.mp4'):
        VIDEO_FILES.append(x)      
