from __future__ import print_function

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import os
import pandas as pd
import glob
import math
import time
import datetime
from motifapi import MotifApi as Motif
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed #for multiprocessing

import traceback
import shutil

"""
def getColumnNames(dateString):
    date = getTimeFromTimeString(dateString)
    if date < getTimeFromTimeString('20180701_010000'):
        XPOS = 'X#centroid (cm)'
        YPOS = 'Y#centroid (cm)'
        XVEL = 'VX#centroid (cm/s)' 
        YVEL = 'VY#centroid (cm/s)'
        SPEED = 'SPEED'
        ACC = 'ACC'
    else:
"""
XPOS = 'X#wcentroid'
YPOS = 'Y#wcentroid'
XVEL = 'VX#smooth#wcentroid'
YVEL = 'VY#smooth#wcentroid'
SPEED = 'SPEED#smooth#wcentroid'
ACC = 'ACCELERATION#smooth#wcentroid'
angVel = 'ANGULAR_A#wcentroid'
angAcc = 'ANGULAR_V#wcentroid'
        
def getTimeFromTimeString(string=None):
    if string == None:
        return datetime.datetime.now()
    elif '_' in string:
        return datetime.datetime.strptime(string, "%Y%m%d_%H%M%S")
    else:
        return datetime.datetime.strptime(time.strftime("%Y%m%d", time.localtime()) + '_' + string, "%Y%m%d_%H%M%S")

def getTimeStringFromTime(TIME=None):
    if TIME == None:
        return datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M%S")
    else:
        return datetime.datetime.strftime(TIME,"%Y%m%d_%H%M%S")

def getModTime(fn):
    t = os.path.getmtime(fn)
    return datetime.datetime.utcfromtimestamp(t)

def smooth(y, x='notDefined', frac=0.05):
    if lowess not in sys.modules:
        from statsmodels.nonparametric.smoothers_lowess import lowess
    if x=='notDefined':
        x = range(len(y))
    filtered = lowess(y, x, frac=frac)
    return filtered[:,1]

def instaSlope(data):
    foo = smooth(data, frac=0.1)
    res = foo - np.roll(foo, 1)
    res[0] =np.nan
    return res 

def loopbio_record(IP, KEY, FN, DUR, META, SN):
    _codec='nvenc-mq'
    api = Motif(IP, KEY)
    
    camInfo = pd.DataFrame(api.call('cameras').items()[0][1])
    camName = camInfo[camInfo.serial == SN]['name'].values[0]
    if "Ximea" in camName:
        SN = camName.split('(')[1][0]
    
    if not (api.call('camera/'+SN)['camera_info']['status'] == 'ready'):
        raise Exception('CAMERA IS ALREADY IN USE')
    #camsn = api.call('cameras')['cameras'][0]['serial']
    api.call('camera/' + SN + '/configure', 
            AcquisitionFrameRate=40.0,
            ExposureTime=2000.0 )
    foo = api.call('camera/' + SN + '/recording/start',
            duration=DUR,
            filename=FN,
            codec=_codec,
            record_to_store=True, 
            metadata=META)
    return foo  
    
def copyAndroidLog(IP, src, dst):
    from subprocess import call
    call(["adb kill-server"], shell=True) #/opt/android-sdk/platform-tools/
    call(["adb start-server"], shell=True)#/opt/android-sdk/platform-tools/
    call(["adb connect " + IP], shell=True)#/opt/android-sdk/platform-tools/
    time.sleep(3)
    cmd = "adb pull -a " + src + " " + dst #/opt/android-sdk/platform-tools/
    try:
        call([cmd], shell=True)
    except:
        return
    time.sleep(2)
    return

def copyWindowsLog(src, dst):
    from subprocess import call
    cmd = "cp " + src + " " + dst
    try:
        call([cmd], shell=True)
    except:
        return
    time.sleep(1)
    return

def sho(i):
    plt.imshow(i)
    plotnice('img')
    plt.show()
    return



def applyParallel(dfGrouped, func, nCores=None):
    """
    pass a pandas dataframe groupby object and a function to call on it. 
    the function must return a single dataframe.
    returns the output of the passed function
    """

    from multiprocessing import Pool, cpu_count
    if nCores == None:
        nCores = cpu_count() - 4
    with Pool(nCores) as p:
        ret_list = p.map(func, [group for name, group in dfGrouped])
    return pandas.concat(ret_list)

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = 'X'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s   ' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print('\n')
    return
    
def createBackgroundImage(DIRECTORY, method='mode'):
    """
    takes directory of mp4s, 
    returns image with modal pixel values from the first video
    """
    import cv2
    if DIRECTORY[-1] != '/':
        DIRECTORY += '/'
        
    firstframe=True
    for vidnum in ['000000.mp4','000001.mp4']:  #LAZY DANNO FIXME    
        vid = cv2.VideoCapture(DIRECTORY + vidnum)
        framecount = int(vid.get(7))
        skipFrames = 17#int(np.round(framecount/100))
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


def process_tracks(list_of_files):
    i = 1
    df = pd.DataFrame()
    for fn in list_of_files:
        ID = fn.split('fish')[-1].split('.')[0]
        d = np.load(fn)
        f =  pd.DataFrame([d[x] for x in d.iterkeys()]).T
        f.columns = d.keys()
        f['trackid'] = ID
        if len(df) == 0:
            df = f.copy()
        else:
            df = pd.concat([df,f], sort=False)
        i += 1    
    return df

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]    
        
def getFrameByFrameData(DIRECTORY, RESUME=True, nCores=8):
    import joblib
    if DIRECTORY[-1] != '/':
        DIRECTORY = DIRECTORY + '/'
    
        
    if os.path.exists(DIRECTORY + 'frameByFrameData.pickle') and RESUME:
        try:
            df = joblib.load(DIRECTORY + 'frameByFrameData.pickle')
            
            if not XPOS in df.columns:
                print(XPOS, "not found in columns. removing tracked data.", DIRECTORY)
                print(df.columns)
                os.remove(DIRECTORY + 'frameByFrameData.pickle') #do not remove fishdata dir here. 
                df = pd.DataFrame() #start fresh
                if os.path.exists(DIRECTORY + 'frameByFrame_complete'):
                    os.remove(DIRECTORY + 'frameByFrame_complete')
                
        except:
            print("Failed to load fbf at getFrameByFrameData()")
            traceback.print_exc()
            os.remove(DIRECTORY + 'frameByFrameData.pickle')
            return
    
    else:
        df = pd.DataFrame()
    i = 1
    for fn in glob.glob(DIRECTORY + 'fishdata/*.csv'):
        ID = fn.split('fish')[-1].split('.')[0]
        if (len(df) >0):
            if not (ID in df['trackid'].values):
                f = pd.read_csv(fn)
                f['trackid'] = ID
                df = pd.concat([df, f], sort=False)
        else:
            f = pd.read_csv(fn)
            f['trackid'] = ID
            df = f#pd.concat([df, f])
        if i%500 == 0:
            #print "processed track number :", i
            df.to_pickle(DIRECTORY + 'frameByFrameData.pickle')
        i +=1
    
    fileList = []
    for fn in glob.glob(DIRECTORY + 'fishdata/*.npz'):
        fileList.append(fn)
        
    # SETUP PARALLEL PROCESSING

    ppe = ProcessPoolExecutor(nCores)
    futures = []
    Results = []
    
    # INITIATE PARALLEL PROCESSES
    chunksize = int(len(fileList)/nCores)
    for files in list(chunks(fileList, chunksize)):
        p = ppe.submit(process_tracks, files)
        futures.append(p)
    
    # COLLECT PROCESSED DATA AS IT IS FINISHED    
    for future in as_completed(futures):
        data = future.result()
        Results.append(data)
    
    #CONCATENATE RESULTS
    df = pd.concat(Results, sort=False)
            

    df = df.loc[df['frame'].notnull() == True, :]
    df['frame'] = df['frame'].astype(int)
    df.replace(to_replace=np.inf, value=np.nan, inplace=True)
    joblib.dump(df, DIRECTORY + 'frameByFrameData.pickle')
    """
    try:
        df.to_pickle(DIRECTORY + 'frameByFrameData.pickle')
    except Exception as e:
        print("ERROR: problem compiling:", DIRECTORY + "frameByFrameData.pickle. trying joblib")
        print(e)
    """    
        
    FINISHED = open(DIRECTORY + 'frameByFrame_complete','w')
    FINISHED.write(getTimeStringFromTime())
    FINISHED.close()

    return df

def crop_stitched_img(img):
    if len(img.shape)==2:
        h,w = img.shape
        return img[100:h-100,100:w-100]
    elif len(img.shape)==3:
        h, w, _ = img.shape
        return img[100:h-100,100:w-100,:]

def plotnice(plotType='standard', ax=plt.gca()):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if plotType == 'hist':
        ax.spines['left'].set_visible(False)
        ax.set_yticks([])
    elif plotType=='img':
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        plt.axis('off')
    return
        
   
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
    
def reportExperimentalSessions():
    df = pd.DataFrame() 
    for x in glob.glob('/media/recnodes/recnode_2mfish/*dotbot*'):
         expID, groupsize, _ , date, time = x.split('/')[-1].split('.')[0].split('_')[:5]
         f = {'expID':expID, 'groupsize':groupsize, 'date':date, 'time':time}
         df = df.append(f, ignore_index=True)
    g = df.groupby(['date', 'expID'])

    foo = pd.merge(g.min(), g.max(), left_index=True, right_index=True)
    foo.columns = ['groupsize','firstExp','groupsize2','lastExp']
    print(foo[['groupsize','firstExp','lastExp']])
    return foo[['groupsize','firstExp','lastExp']]

def reportExperimentGroups(fileList):
    df = pd.DataFrame({'names':fileList})
    df[['groupsize','date','time']] = pd.DataFrame([np.array(x.split('/')[-1].split('.')[0].split('_'))[[1,3,4]].astype(int) for x in df['names']])
    print(df.groupby('groupsize').count()['names'])
    print("Date range: "+ str(df['date'].min())+ str(df['date'].max()))
    return

