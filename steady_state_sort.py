import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd
import numpy as np
from scipy import stats
import scipy
import stim_handling as stims
from utilities import *
import imgstore



XPOS = 'X#wcentroid'
YPOS = 'Y#wcentroid'
XVEL = 'VX#smooth#wcentroid'
YVEL = 'VY#smooth#wcentroid'
SPEED = 'SPEED#smooth#wcentroid'
ACC = 'ACCELERATION#smooth#wcentroid'
angVel = 'ANGULAR_A#wcentroid'
angAcc = 'ANGULAR_V#wcentroid'


def get_hull_area(g, q=0.95):
    """
    pass a df grouped by FrameNumber
    """
    areas = []
    frames = []
    densities = []
    for frame, data in g:
        distances = distance_from_point(data[XPOS],data[YPOS])
        dQ = data.loc[distances < distances.quantile(q),:]
        if len(dQ) <3:   
            area = np.nan
            density = np.nan
        else:
            area = scipy.spatial.ConvexHull(list(zip(dQ[XPOS],dQ[YPOS]))).area
            density = float(area/len(dQ))
        areas.append(area)
        frames.append(frame)
        densities.append(density)
    return pd.DataFrame({'FrameNumber':frames,'Area':areas, 'Density': densities})
    
def distance_from_point(xx, yy, cx=None, cy=None):
    #returns distance from given points (xx and yy) and a defined point, defaults to centre (cx, cy)
    if cx==None:
        cx = xx.median()
    if cy == None:
        cy = yy.median()
    return np.sqrt((xx-cx)**2 + (yy-cy)**2)
        

def drop_bad_points(fbf, arena_centre=(160.0,160.0)):
    fbf['radius'] = np.sqrt((fbf[XPOS]-arena_centre[0])**2 + (fbf[YPOS]-arena_centre[1])**2) 
    fbf = fbf.loc[fbf['radius'] <215, :]
    fbf = fbf.loc[fbf[XPOS] < 315,:]  #FIXME hardcoding bad
    return fbf

def sync_by_stimStart(df, ID, col='speed'):
    """
    pass a df with stim information
    returns the df with rotation values adjusted for direction so rotation of new stim is positive
    """
    df = df.sort_values('Time')
    df.reset_index(inplace=True)
    df = df[:-10] #drop end to avoid dealing with annoying NaN cases #lazy #FIXME
    
    df.loc[:,'stimStart'] = 0
    firstStim = df.loc[df['Time'] < df['Time'].median(), 'speed'].idxmax()
    df.loc[firstStim, 'stimStart'] = 1
    df.loc[:,'stimEnd'] = 0
    lastStim = df.loc[df['Time'] > df['Time'].median(), 'speed'].idxmin()
    df.loc[lastStim, 'stimEnd'] = 1
    
    alignPoints = list(df[df['stimStart'] == 1]['Timestamp'].values)
    #df = df[df[col].isnull() == False]
    i = alignPoints[0]
    df['syncTime'] = pd.to_timedelta(df['Timestamp']-i,'s') 
    df['trialID'] = ID
    DIRECTION = np.sign(np.median(df['dir']))
    df[df.columns[['otation' in f for f in df.columns]]] *= DIRECTION
    
    return df

def sync_by_reversal(df, ID, col='dir'):
    """
    pass a df with stim information
    returns the df with rotation values adjusted for direction so rotation of new stim is positive
    """
    df = df.sort_values('Timestamp').reset_index()
    df = df[:-10]
    df['reversal'] = 0
    reversals = df[abs(df[col] - df.shift()[col]) ==2].index
    df.loc[reversals, 'reversal'] = 1
    df.loc[df['Time'] > 300, 'reversal'] = 0 #FIXME this is a hack solution to sort out ends
    df['firstStim'] = 0
    firstStim = df[df['Time'] < df['Time'].median()]
    firstStim = firstStim[abs(firstStim[col] - firstStim.shift()[col]) ==1].index
    df.loc[firstStim, 'firstStim'] = 1
    df['lastStim'] = 0
    lastStim = df[df['Time'] > df['Time'].median()]
    lastStim = lastStim[abs(lastStim[col] - lastStim.shift()[col]) ==1].index
    df.loc[lastStim, 'lastStim'] = 1
    trials = pd.DataFrame()
    trialID = 0    
    alignPoints = list(df[df['reversal'] == 1]['Timestamp'].values)
    for i in alignPoints:
        data = df.loc[df['Timestamp'].between(i-10.0, i+60.0), :]
        data['syncTime'] = pd.to_timedelta(data['Timestamp']-i,'s') 
        data['trialID'] = ID + '_' + str(trialID)
        data['date'] = ID.split('_')[0]
        DIRECTION = np.sign(np.median(data['dir']))
        data[data.columns[['otation' in f for f in data.columns]]] *= DIRECTION
        trialID += 1
        trials = pd.concat([trials, data], axis=0)        
    return trials


def rank_on_column(df, col, nRanks):
    """
    pass a df, returns an index-matched series grouping col into nRanks groups
    """
    bounds = np.linspace(0,1,nRanks+1)
    df = df.copy()
    df['rank'] = np.nan
    for i in range(nRanks):
        if i == 0:
            INKL=True
        else:
            INKL=False
        df.loc[df[col].between(df.quantile(bounds[i])[col], 
                               df.quantile(bounds[i+1])[col] + 1e5, #tiny hack for inclusive upper bound
                               inclusive=INKL),
              'rank'] = i
    return df['rank']


def get_area(fbf):
    g = fbf.groupby('FrameNumber')
    areaDF = get_hull_area(g)
    return areaDF



if __name__ == "__main__":
    import argparse
    import glob
    import os
    import joblib

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=False, default = '/media/recnodes/recnode_2mfish',help='path to directory')
    parser.add_argument('--handle', type=str, required=True, 
                        help='provide unique identifier  to select a subset of directories.')    

    args = parser.parse_args()
    


    if 0:#os.path.exists('/media/recnodes/Dan_storage/' + args.handle + '_sorted_by_final_minute.pickle'):
        results = pd.read_pickle('/media/recnodes/Dan_storage/' + args.handle + '_sorted_by_final_minute.pickle')
    else:
        results = pd.DataFrame()
        
    for MAIN_DIR in glob.glob(args.dir + '/'+ args.handle + '*.stitched'):
        if not os.path.exists(MAIN_DIR + '/track/perframe_stats.pickle'):
            continue
        
        expID = MAIN_DIR.split('/')[-1].split('.')[0]
        exp, groupsize, _, trialID = expID.split('_', 3)
        #don't repeat if already done
        if trialID in results.index:
            continue 
        try:        

            store = imgstore.new_for_filename(MAIN_DIR + '/metadata.yaml')
            fbf = pd.read_pickle(MAIN_DIR+'/track/perframe_stats.pickle') 
            if len(fbf) < 1000:
                fbf = joblib.load(MAIN_DIR+'/track/perframe_stats.pickle') 
            
            if not 'FrameNumber' in fbf.columns: 
                ret, fbf = stims.sync_data(fbf, 
                                stims.get_logfile(MAIN_DIR), 
                                store) 
            
            #fbf = drop_bad_points(fbf)                               
            if 'coherence' in expID:   
                synced = sync_by_stimStart(fbf, trialID)                             
            elif 'reversal' in expID:
                synced = sync_by_reversal(fbf, trialID)
            
            sort_section = synced[synced.syncTime.between(np.timedelta64(240, 's'), np.timedelta64(300,'s'))]
            
            for group, data in sort_section.groupby('trialID'):
                s = pd.Series(data.median(), name=group)
                s['exp'] = exp
                s['groupsize'] = groupsize
                results = results.append(s)
                results.to_pickle('/media/recnodes/Dan_storage/' + args.handle + '_sorted_by_final_minute.pickle')
                print(s)
        except Exception as e:
            print('failed:', expID, e)

    results.drop('FrameNumber',axis=1, inplace=True)
    for group, data in results.groupby(['groupsize','coh']):
        results.loc[data.index, 'rotation_rank'] = rank_on_column(data, 'median_dRotation_cArea',3)
        results.loc[data.index, 'entropy_rank'] = rank_on_column(data, 'entropy_Ra', 3)

    
    #names = pd.DataFrame([i.split('_',3) for i in results.index],
    #               columns=['exp','groupsize','dotbot','trialID'])
    #r = results.reset_index(drop=True).merge(names, 
    #                                            left_index=True,
    #                                            right_index=True) 
    results.to_pickle('/media/recnodes/Dan_storage/' + args.handle + '_sorted_by_240-300_complete.pickle')                          

