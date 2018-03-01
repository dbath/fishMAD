import numpy as np
import cv2
import yaml




def calibrate(VIDEO_FILE, CHECKERSHAPE, DESTFILE):
    checkerShape = CHECKERSHAPE
    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((checkerShape[0]*checkerShape[1],3), np.float32)
    objp[:,:2] = np.mgrid[0:checkerShape[0],0:checkerShape[1]].T.reshape(-1,2)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.


    cap = cv2.VideoCapture(VIDEO_FILE)
    found = 0
    while (found < 15):  # Here, 10 can be changed to whatever number you like to choose
        ret, img = cap.read() # Capture frame-by-frame
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, checkerShape,None)

        cap.set(1, cap.get(1)+40)
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)   # Certainly, every loop objp is the same, in 3D.
            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
            imgpoints.append(corners2)
            found += 1


    # When everything done, release the capture
    cap.release()
    #cv2.destroyAllWindows()

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    # It's very important to transform the matrix to list.

    data = {'camera_matrix': np.asarray(mtx).tolist(), 'dist_coeff': np.asarray(dist).tolist()}

    with open(DESTFILE, "w") as f:
        yaml.dump(data, f)
    print 'Calibration complete: ', DESTFILE.split('/')[-1]
    return 




if __name__ == "__main__":

    import argparse
    import glob
    from utilities import *
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=True, help='path to directory containing checker vids')
    parser.add_argument('--checkersize', type=str, required=False, default='6x6', help='size of checkerboard, default is 6x6')

                
    args = parser.parse_args()
    
    CHECKERSIZE = tuple([int(k) for k in args.checkersize.split('x')])
    
    for vid in glob.glob(slashdir(args.dir) + '*.mp4'):
        DATETIME = '_'.join(vid.split('/')[-1].split('.')[0].rsplit('_',2)[1:])
        SERIAL = vid.split('/')[-1].split('.')[-2]
        calibrate(vid, CHECKERSIZE, '/home/dan/fishMAD/camera_calibrations/'+'_'.join([DATETIME,SERIAL])+'.yaml') 











