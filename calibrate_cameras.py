import numpy as np
import cv2
import yaml
import matplotlib.pyplot as plt
import pandas as pd



def showFeatures(img, df, fn):
     plt.imshow(img)

     plt.scatter(df['x'], df['y'], color='r', s=2)
     if fn == 'nosave':
        plt.show()
     else:
        plt.savefig(fn, layout='Tight')
     return

def coords(a):
    # where a is a cornerSubPix Array
    xs = []
    ys = []
    for x in range(len(a)):
        xs.append(a[x][0])
        ys.append(a[x][1])
    df = pd.DataFrame({'x':xs, 'y':ys})
    return df
    
def getPointsList(a):
    # where a is a cornerSubPix Array
    return pd.DataFrame([a[x][0] for x in range(len(a))]) 
     
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
    errorcount = 0
    while (found < 90):  #  can be changed to whatever number you like to choose
    
        ret, img = cap.read() # Capture frame-by-frame
        if ret == True:
            try:
                gray = img[:,:,0]#cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            except:
                print "error here"
                continue

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, checkerShape,None)

            #
            # If found, add object points, image points (after refining them)
            if ret == True:
                objpoints.append(objp)   # Certainly, every loop objp is the same, in 3D.
                corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
                imgpoints.append(corners2)
                found += 1
                cap.set(1, cap.get(1)+2)
                lastImg = img
                #showFeatures(img, pd.DataFrame(getPointsList(corners2) ,columns=['x','y']), 'nosave')
        else:
            errorcount +=1
            if errorcount > 100:
                print "Could not generate full calibration file: ", DESTFILE.split('/')[-1]
                break
                
    df = pd.concat([getPointsList(imgpoints[x]) for x in range(len(imgpoints))])
    df.columns = ['x','y']
    df.to_pickle(VIDEO_FILE.rsplit('.',1)[0] +'.pickle')

    # When everything done, release the capture
    cap.release()
    #cv2.destroyAllWindows()

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    # It's very important to transform the matrix to list.

    data = {'camera_matrix': np.asarray(mtx).tolist(), 'dist_coeff': np.asarray(dist).tolist()}

    showFeatures(lastImg, df, VIDEO_FILE.rsplit('.',1)[0] +'.png')
    
    with open(DESTFILE, "w") as f:
        yaml.dump(data, f)
        
    print 'Calibration complete: ', DESTFILE.split('/')[-1]

    
    
    return 




if __name__ == "__main__":

    import argparse
    import glob
    from utilities import *
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=False, default='/media/recnodes/recnode_2mfish/',
			 help='path to directory containing checker vids')
    parser.add_argument('--handle', type=str, required=True, help='unique identifier that marks the files to use for calibration. Ideally use the timestamp of the recording, ie "20180808_153229".'
    parser.add_argument('--checkersize', type=str, required=False, default='6x6', help='size of checkerboard, default is 6x6')
    parser.add_argument('--saveas', type=str, required=False, default='notDefined', help='name for calibration, including date time string, ex: 20180404_123456')

                
    args = parser.parse_args()
    
    CHECKERSIZE = tuple([int(k) for k in args.checkersize.split('x')])
    
    
    
    for vid in glob.glob(slashdir(args.dir) + '*' + args.handle + '*.mp4'):
        if args.saveas == 'notDefined':
            DATETIME = '_'.join(vid.split('/')[-1].split('.')[0].rsplit('_',2)[1:])
            SERIAL = vid.split('/')[-1].split('.')[-2]
            SAVE_AS = '_'.join([DATETIME,SERIAL])
        else:
            SAVE_AS = '_'.join([args.saveas, vid.split('.')[-2]])
            
        
        calibrate(vid, CHECKERSIZE, '/home/dan/fishMAD/camera_calibrations/'+SAVE_AS+'.yaml') 











