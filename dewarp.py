import numpy as np
import cv2
import glob
import yaml
from utilities import *

class Dewarp:

    def __init__(self, VIDEOFILE):
        self.vidfile = VIDEOFILE
        self.video_timestamp = '_'.join(VIDEOFILE.split('/')[-1].split('.')[0].rsplit('_',2)[1:])
        self.startTime = getTimeFromTimeString(self.video_timestamp)
        self.camSerial = VIDEOFILE.split('/')[-1].split('.')[-2]
        self.calibrationFile = self.selectCalibrationFile()
        
        k, d = self.loadCameraConfig(self.calibrationFile)
        
        self.cameraMatrix = np.array(k)
        self.cameraDistortion = np.array(d)
        
        print "Dewarping video: ", self.vidfile, "using calibration: ", self.calibrationFile
        
        return
    
    def selectCalibrationFile(self):
        """
        returns the calibration file from the correct camera 
        from the most recent calibration before the video was created.
        """
        fileList = []
        times = []
        for x in glob.glob('/home/dan/fishMAD/camera_calibrations/*.yaml'):
            fileList.append(x)
            times.append(getTimeFromTimeString(x.split('/')[-1].split('.')[0].rsplit('_',1)[0]))
        df = pd.DataFrame({'filename':fileList, 'times':times})
        calTime = df[df.times < self.startTime].max()['filename'].split('/')[-1].rsplit('_',1)[0]
        
        return '/home/dan/fishMAD/camera_calibrations/' + calTime + '_' + self.camSerial + '.yaml'
        
    def loadCameraConfig(self, CALIBRATION):
    
        with open(CALIBRATION) as f:
            loadeddict = yaml.load(f)

        mtxloaded = loadeddict.get('camera_matrix')
        distloaded = loadeddict.get('dist_coeff')
        
        return mtxloaded, distloaded

    def undistort(self, img): 
        if not hasattr(self, 'newcamera'):
            h,w = img.shape[:2]
            self.newcamera, roi = cv2.getOptimalNewCameraMatrix(self.cameraMatrix, self.cameraDistortion, (w,h), 0) 
        
        return cv2.undistort(img, self.cameraMatrix, self.cameraDistortion, None, self.newcamera)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=True, help='path to videos')
    parser.add_argument('--saveas', type=str, required=False, default='notAssigned', help='output filename')
    args = parser.parse_args()
    
    VIDEO_FILES = []
    
    for x in glob.glob(slashdir(args.dir) + '*.mp4'):
        VIDEO_FILES.append(x)
    
    for VIDEO_FILE in VIDEO_FILES:
        if args.saveas == 'notAssigned':
            fn, ext =  VIDEO_FILE.rsplit('.',1)
            OUTPUT_FILE =fn + '_dewarped.' + ext
        else:
            OUTPUT_FILE = VIDEO_FILE.rsplit('/',1)[0] + args.saveas
        
        video = cv2.VideoCapture(VIDEO_FILE)
        FPS = int(video.get(5))
        framecount = video.get(7)
        videoformat = video.get(6)
        videoSize = (int(video.get(3)), int(video.get(4)))  
        
        DEWARP = Dewarp(VIDEO_FILE)
        
        out = cv2.VideoWriter(OUTPUT_FILE, cv2.VideoWriter_fourcc('a','v','c','1'),  FPS, videoSize)
        
        while video.isOpened():
            ret, img = video.read()
            if ret == True:
                newimg = DEWARP.undistort(img)
                out.write(newimg)
            else:
                break        
          
        video.release()
    print "done."      

