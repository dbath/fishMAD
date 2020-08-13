
import stim_handling as stims
import pandas as pd
import joblib
import numpy as np
import scipy
import imgstore
from concurrent.futures import ProcessPoolExecutor, as_completed #for multiprocessing
from utilities import *
from collections import defaultdict
import traceback
from multiprocessing import Process
from scipy.stats import spearmanr

XPOS = 'X#wcentroid'
YPOS = 'Y#wcentroid'
XVEL = 'VX#smooth#wcentroid'
YVEL = 'VY#smooth#wcentroid'
SPEED = 'SPEED#smooth#wcentroid'
ACC = 'ACCELERATION#smooth#wcentroid'
angVel = 'ANGULAR_A#wcentroid'
angAcc = 'ANGULAR_V#wcentroid'



def packingfraction(area, N):
    FISH_AREA = 14.5  #based on 175 pixels per fish. determined empirically from data from T.Water 20200218
    return (N*FISH_AREA)/area

def sync_rotation(r, log, store):
    """
    pass: r - any df with frame number (0>N) as index
          log - a corresponding log file (from get_logfile())
          store - imgstore object of corresponding video
    returns:  df with frame numbers from camera, timestamps, and stim info
    """    

    foo = stims.get_frame_metadata(r, store)
    foo.reset_index(drop=True, inplace=True)

    bar = foo.merge(log, how='outer') 
    bar = bar.sort_values('Timestamp')
    bar = bar.fillna(method='ffill')  #forward fill data from log to tracking data
    bar['speed'] = bar['speed'].fillna(method='ffill').fillna(0)
    bar['dir'] = bar['dir'].fillna(method='ffill').fillna(method='bfill')
    #for some reason the following step took forever? 
    #bar.loc[:,'Time'] = (bar.loc[:,'Timestamp'] - bar.loc[0,'Timestamp'])
    #if 'R' in bar.columns:
    #    bar['R'] = bar['R']*bar['dir']
    bar = bar.loc[foo.index] #drop rows from log entries 
    bar = bar.sort_values('Timestamp') #sort again because lazy danno
    bar.reset_index(drop=True, inplace=True)
    return bar  


    
def distance(A, B):
    return np.sqrt((A[0]-B[0])**2 + (A[1]-B[1])**2)

def prune_by_distance(f0, T='twostd'):
    """
    f0: from a single frame including "edgeList" (the trackids of neighbours) and "edgeLengths" (an ordered list of euclidian distance to neighbours)
    T: the threshold distance above which edges will be pruned. default is 2 std's above the median for the entire frame. alternatively, pass a numeric value for the threshold.
    """

    if T=='twostd':
        e = np.concatenate(f0.edgeLengths.values)
        T = np.mean(e) + 2*e.std()     
    vals = np.array(f0.edgeLengths) 
    neiList = np.array(f0.edgeList) 
    keepers = np.array([k <= T for k in f0.edgeLengths])  

    pruned_vals = [vals[k][keepers[k]] for k in range(len(vals))]
    pruned_neilist = [neiList[k][keepers[k]] for k in range(len(neiList))]
    return pruned_neilist, pruned_vals
    
def neighbourhoodWatch(frameData, _focalID):
    """
    pass a df representing all data to be included, typically for a single frame, indexed by trackid as int
    
    pass the trackid of the focal indiv 
    
    returns:
    
    local polarization and rotation of the neighbourhood relative to focal indiv
    
                   
    
    """
    #load the data in relevant slices
    focal = frameData.loc[_focalID]
    neighbourIDs = list(focal['edgeList'])
    #print(neighbourIDs)
    neighbours = frameData.loc[neighbourIDs]
    neighbourhood = frameData.loc[np.append(neighbourIDs, int(_focalID))]
    
    #calculate properties of the neighbourhood
    if len(neighbours) <2:
        AREA = np.nan
    elif len(neighbours) <3: #can't do convex hull, so include self:
        AREA = scipy.spatial.ConvexHull([*zip(neighbourhood[XPOS], neighbourhood[YPOS])]).volume
    else:
        AREA = scipy.spatial.ConvexHull([*zip(neighbours[XPOS], neighbours[YPOS])]).volume #ConvexHull.volume returns area because flatearth
    PACKING_FRACTION = packingfraction(AREA, len(neighbourhood)) 
    NEIGHBOUR_DIST = np.median(focal['edgeLengths'])

    Rmedian = np.median(neighbours.R)
    #Rmean = np.mean(neighbours.R) #dropped to save 80us
    Rscore = ((neighbourhood['R'].rank()-1)/len(neighbours))[_focalID] # =1 for highest, 0 for lowest
    
    polarization = abs(np.sqrt((neighbourhood['uVX'].mean())**2 + (neighbourhood['uVY'].mean())**2))
    #uM = neighbourhood[['uVX','uVY']].mean() # /polarization #unit vector of mean direction
    #Pscore = (1-((abs(neighbourhood[['uVX','uVY']] - uM)).sum(axis=1).rank()-1)/(len(neighbours)))[_focalID] 
    
    #Polarization-Distance correlation: is the angle similarity to each neighbour correlated with distance?
    #PDcor = spearmanr(focal.edgeLengths, np.sqrt((focal.uVX - neighbours.uVX)**2 + (focal.uVY - neighbours.uVY)**2))[0]
    PDcor = spearmanr(focal.edgeLengths, (focal.uVX - neighbours.uVX)**2 + (focal.uVY - neighbours.uVY)**2)[0] #drop sqrt for speed
    
    #below are the proper calculations for uM and Pscore. Since we are ranking,
    # it is ok to remove sqrt, **2, and divide-by-scalars. this saves 1ms total. 
    
    #uM = neighbourhood[['uVX','uVY']].mean() /polarization #unit vector of mean direction
    #Pscore = (1-(np.sqrt(((neighbourhood[['uVX','uVY']] - uM)**2).sum(axis=1)).rank()-1)/(len(neighbours)))[_focalID] #this is the proper way
    
    Speedscore = (1-((focal[SPEED] - neighbourhood[SPEED]).rank()-1)/len(neighbours))[_focalID]

    NN = np.array([frameData.frame.mean(),
                   focal.trackid,
                   NEIGHBOUR_DIST,
                   AREA,
                   PACKING_FRACTION,
                   Rmedian,
                   Rscore,
                   polarization,
                   PDcor,
                   Speedscore
                   ]).astype(float)

    """
    NN = {'frame': frameData.frame.mean() ,
          'trackid': focal.trackid,
          'neighbourDist': NEIGHBOUR_DIST,
          'localArea':AREA,
          'localPackingFraction':PACKING_FRACTION,
          'localMedianRotation':Rmedian,
          #'localMeanRotation':Rmean,
          'localRScore':Rscore,
          'localPolarization':polarization,
          'localPScore':PDcor,
          'localSpeedScore':Speedscore,
          }
    """                 
    return NN


def process_chunk(df):
    maxFrame = df.frame.max()
    if maxFrame%args.maxthreads == 0:
        progressbar = True
    else:
        progressbar = False  
    
    frames = df.groupby('frame')

    growingArray = np.zeros((1,10))
    for f, frameData in frames:
        frameData = frameData.copy()
        frameData.index = frameData['trackid'].astype(int)
        #pruned_neighbourIDs, pruned_neighbourDistances = prune_by_distance(frameData)
        try:
            frameData['edgeList'], frameData['edgeLengths'] = prune_by_distance(frameData)
        except:
            print('prune_by_distance failed at:', f)
            frameData['edgeList'] = np.nan
            frameData['edgeLengths'] = np.nan
        for ID in frameData.index:
            growingArray = np.vstack([growingArray,neighbourhoodWatch(frameData, ID)])  
        if progressbar == True:
            printProgressBar(f,maxFrame, prefix='processing: ')
    chunk = pd.DataFrame(growingArray[1:])
    chunk.columns = ['frame','trackid','neighbourDist','localArea',
                         'localPackingFraction','localMedianRotation',
                         'localRscore','localPolarization','localPDcor',
                         'localSpeedScore']   
    return chunk

#space junk?
#H = lambda x: pd.Series(x.groupby('ndisdig')['R_stimcorrected'].mean())    
#plt.imshow(ts.resample('1s').apply(H).unstack().T, origin='lower') 



if __name__ == "__main__":
    import os, datetime
    import argparse
    import utilities
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=False, default = '/media/recnodes/recnode_2mfish',help='path to directory')
    parser.add_argument('--handle', type=str, required=False, default='_dotbot_', 
                        help='provide unique identifier (or comma-separated list) to select a subset of directories.')
    parser.add_argument('--maxthreads', type=int, required=False, default=20, 
                        help='maximum number of threads to use in parallel.')

                
    args = parser.parse_args()
    
    HANDLE = args.handle
        
    nCores = args.maxthreads 
    DATETIME = utilities.getTimeFromTimeString('20200604_090000') #FIXME hardcoded
    for MAIN_DIR in glob.glob(args.dir + '/*' + HANDLE + '*.stitched'):  
        MAIN_DIR = slashdir(MAIN_DIR)

        if os.path.exists(MAIN_DIR + 'track/localData_FBF.pickle'):
            if datetime.datetime.fromtimestamp(os.path.getmtime(MAIN_DIR + 'track/localData_FBF.pickle')) > DATETIME:
                continue
        elif os.path.exists(MAIN_DIR + 'track/localData_FBF_1.pickle'): #FIXME
            continue
        #MAIN_DIR = '/media/recnodes/recnode_2mfish/reversals3m_128_dotbot_20181211_151201.stitched/'
        if not os.path.exists(MAIN_DIR + 'track/network_FBF.pickle'):
            print("no network_FBF.pickle found: ", MAIN_DIR.split('/')[-2])
            continue
        print("processing ", MAIN_DIR)
        nfbf = joblib.load(MAIN_DIR + 'track/network_FBF.pickle')
        print("loaded data with size", nfbf.shape)
        nfbf[SPEED] = np.sqrt(nfbf[XVEL]**2 + nfbf[YVEL]**2) 
        nfbf['uVX'] = nfbf['VX#smooth#wcentroid']/nfbf[SPEED]
        nfbf['uVY'] = nfbf['VY#smooth#wcentroid']/nfbf[SPEED]


        log = stims.get_logfile(MAIN_DIR)
        store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml')
        nfbf = sync_rotation(nfbf, log, store)
        nfbf.reset_index(drop=True, inplace=True)
        nfbf = nfbf.loc[nfbf['frame'] <= 20000,:] #FIXME this is another hack to reduce memory usage

	#what a ridiculous solution to running out of memory:#FIXME
        
        for COUNT in range(10):
            DATA = nfbf.loc[nfbf.frame.between(np.quantile(nfbf.frame, COUNT*0.1), np.quantile(nfbf.frame, (COUNT+1)*0.1)),:]
            #elif COUNT == 1:
            #    DATA = nfbf.loc[nfbf.frame >= np.median(nfbf.frame)]
            print("setting parallel processes")
            ppe = ProcessPoolExecutor(nCores)
            futures = []
            Results = []
            # INITIATE PARALLEL PROCESSES
            DATA['coreGroup'] = DATA['frame']%nCores
            DATA.reset_index(inplace=True, drop=True)
            for n in range(nCores):
                p = ppe.submit(process_chunk, DATA.loc[DATA['coreGroup'] == n, :])
                futures.append(p)
            # COLLECT PROCESSED DATA AS IT IS FINISHED   
            for future in as_completed(futures): 
                Results.append(future.result())
            #CONCATENATE RESULTS
            localData = pd.concat(Results)
            localData.to_pickle(MAIN_DIR + 'track/localData_FBF_' +str(COUNT) + '.pickle')
	            
