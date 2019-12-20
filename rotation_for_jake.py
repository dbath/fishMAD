
### JAKE USE THIS  ####




def load_rotation_data(filename):
    data = np.load(filename)
    groupsize, coherence, trialID = filename.split('/')[-1].split('_', 2)
    return groupsize, coherence, trialID, data

class Trial(object):
    def __init__(self, pathToNpz):
        DATA = np.load(pathToNpz, allow_pickle=True)
        self.rotationA = DATA['rA']
        self.rotationM = DATA['rM']
        self.prestim = DATA['prestim'].item()
        self.metadata = DATA['meta'].item()
        self.trialID = self.prestim['trialID']

    
    
### JAKE JUST FYI, HOW I MADE THIS ###

import stim_handling as stims  #github.com/dbath/fishMAD
import imgstore # pip install imgstore
import joblib
import pandas as pd
import numpy as np


def sync_by_stimStart(df, ID, col='speed', REVERSALS=False):
    """
    pass a df with stim information
    returns the df with rotation values adjusted for direction so rotation of new stim is positive
    """
    df = df.sort_values('Time')
    df.reset_index(inplace=True)
    df = df[:-10] #drop end to avoid dealing with annoying NaN cases #lazy #FIXME
 
    if REVERSALS:
        XLIM = (-10,60)
        reversals = df[abs(df[col] - df.shift()[col]) ==2].index
        df.loc['reversal'] = 0
        df.loc[reversals, 'reversal'] = 1
        df.loc[df['Time'] > 300, 'reversal'] = 0
        alignPoints = list(df[df['reversal'] == 1]['Timestamp'].values)
    else:
        XLIM = (-30,400)
        df.loc[:,'stimStart'] = 0
        firstStim = df.loc[df['Time'] < df['Time'].median(), 'speed'].idxmax()
        df.loc[firstStim, 'stimStart'] = 1
        df.loc[:,'stimEnd'] = 0
        lastStim = df.loc[df['Time'] > df['Time'].median(), 'speed'].idxmin()
        df.loc[lastStim, 'stimEnd'] = 1
        alignPoints = list(df[df['stimStart'] == 1]['Timestamp'].values)

    trials = pd.DataFrame()
    trialID = 0    
    #df = df[df[col].isnull() == False]
    for i in alignPoints:
        data = df.loc[df['Timestamp'].between(i+XLIM[0], i+XLIM[1]),:].copy()
        for column in data.columns:
            if 'otation' in column: #what a silly hack to catch all the different names for rotation. lazy
                data[column] = data[column]*data['dir'].median() 
        data['syncTime'] = pd.to_timedelta(data['Timestamp']-i,'s') 
        data['trialID'] = ID + '_' + str(trialID)
        data['date'] = ID.split('_')[0]   
        data['startTime'] = ID.split('_')[1]   
        trialID += 1
        trials = pd.concat([trials, data], axis=0)
    return trials



def save_rotation_data(expFileName):
    try:
        fbf = pd.read_pickle(expFileName + '/track/perframe_stats.pickle')
        rot = pd.read_pickle(expFileName + '/track/rotationOrders_cArea.pickle')
        ret, pf = stims.sync_data(fbf, 
                          stims.get_logfile(expFileName), 
                          imgstore.new_for_filename(expFileName + '/metadata.yaml')
                          )
        synced = sync_by_stimStart(pf)                  
        ix = synced[synced.syncTime.between(np.timedelta64(30, 's'), np.timedelta64(300,'s'))].index 
        DIR = synced.loc[ix.min()+100,'dir']     
        data = np.concatenate([rot[x] for x in range(ix.min(), ix.max())]) *DIR
        COH = str(np.around(pf.coh.mean(), 1)) 
        GS = expFileName.split('/')[-1].split('_')[1] 
        ID = expFileName.split('/')[-1].split('_',3)[-1].split('.')[0]
        np.save('/media/recnodes/Dan_storage/191205_rotation_data/' + GS + '_' + COH + '_' + ID + '.npy', data)

        return 1
    except:
        return 0

def rotationOrder(centreX, centreY, posX, posY, velX, velY):
    """
    centre - a single point marking the axis of rotation
    pos - position of agents (1 per agent)
    vel - velocity of agents (1 per agent)
    
    Returns: 1d array of rotation order values
    """
    CX = posX - centreX
    CY = posY - centreY
    radius = np.sqrt(CX**2 + CY**2)
    uCX = CX / radius # X component of unit vector R
    uCY = CY / radius # Y component of unit vector R        
    rotation = np.cross(pd.DataFrame({'uCX':uCX,'uCY':uCY}), pd.DataFrame({'velX':velX, 'velY':velY}))

    return rotation

area = pd.read_pickle('/media/recnodes/Dan_storage/191217_prestim_area_and_density.pickle') 

def get_Tseries(expFileName):

    expID = expFileName.split('/')[-1].split('_',3)[-1].split('.')[0]
    if 'reversal' in expFileName:
        REVERSAL = True
        prestim_frames = 400
        poststim_frames = 2400
    else:
        REVERSAL = False
        prestim_frames = 1200
        poststim_frames = 16000
        
    fbf = pd.read_pickle(expFileName + '/track/frameByFrameData.pickle')
 
    pf = pd.read_pickle(expFileName + '/track/perframe_stats.pickle')
    sy = sync_by_stimStart(pf,expID, REVERSALS=REVERSAL)
    
    for ID, data in sy.groupby('trialID'):
        frame_0 = data.loc[data['syncTime'] == abs(data.syncTime).min(), 'frame'].values[0]
        md = data.loc[frame_0-prestim_frames:frame_0+poststim_frames]
        prestim = data.loc[data['frame'] < frame_0, :]
        psMeta = dict(prestim[prestim.columns[prestim.dtypes == 'float64']].fillna(0).mean())
        
        a = area[area.index == ID]
        if len(a) > 0:
            for col in ['Area','Area_rank','Density','Density_rank','groupsize','trialID']:
                psMeta[col] = a[col][0]
        else:
            psMeta['trialID'] = ID
        d = fbf[fbf['frame'].between(frame_0-prestim_frames, frame_0+poststim_frames)]
        rotA = d.groupby(['frame','trackid'])['rotation_cArea'].mean().unstack()
        rotM = d.groupby(['frame','trackid'])['rotation_cMass'].mean().unstack()
        stim = data.groupby('frame')['speed']#FIXME
        meta = {}
        
        FN = '/media/recnodes/Dan_storage/Jake_TS/'+ expFileName.split('/')[-1].rsplit('_',2)[0] + '_' + ID + '.npz'
        
        np.savez(FN, rA=rotA, rM=rotM, prestim=psMeta, meta=meta)
 
    return 
    
        
if __name__ == "__main__":
    import glob
    for fn in glob.glob('/media/recnodes/recnode_2mfish/*coherencetestangular3m*dotbot*.stitched'):
        ret = save_rotation_data(fn)        
        if not ret:
            print("failed for: ", fn.split('/')[-1])








