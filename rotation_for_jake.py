
### JAKE USE THIS  ####

EXCLUDE_DAYS=['20181026', #a day that will live on in infamy
              '20191022' #recordings were too short this day.
             ]


DEARCHIVE = ['coherencetestangular3m_256_dotbot_20181214_135201',
            'coherencetestangular3m_512_dotbot_20181018_111202',
            'coherencetestangular3m_512_dotbot_20181017_153202'
             ]

PERMISSIONS_PROBLEMS = ['media/recnodes/recnode_2mfish/coherencetestangular3m_4_dotbot_20190913_145201.stitched']

def load_rotation_data(filename):
    data = np.load(filename)
    groupsize, coherence, trialID = filename.split('/')[-1].split('_', 2)
    return groupsize, coherence, trialID.split('.np')[0], data

class Trial(object):
    def __init__(self, pathToNpz, maxlength=13200):
        self.experiment, self.groupsize, self.coherence, _ = pathToNpz.split('/')[-1].split('_',3)
        DATA = np.load(pathToNpz, allow_pickle=True)
        self.rotationA = DATA['rA'][:maxlength]
        self.rotationM = DATA['rM'][:maxlength]
        self.prestim = DATA['prestim'].item()
        self.metadata = DATA['meta'].item()
        self.trialID = self.prestim['trialID']
        self.coherence_TS = DATA['coherence'][:maxlength]
        self.direction_TS = DATA['direction'][:maxlength]
        self.speed = DATA['speed'][:maxlength]
        self.direction = np.sign(self.direction_TS.mean())
        if len(self.rotationA) < maxlength:
            print('truncated file:', self.trialID, 'firststim', str(abs(self.direction_TS).argmax()), 'length:', len(self.rotationA))
        return

    def report(self):
        print(str(abs(self.direction_TS).argmax()), len(self.rotationA))

        
class Rotation(Trial):
    def __init_(self, data):
        self.data = data
            
    def normed(self):
        return self.data*np.median(self.direction)
    
### JAKE JUST FYI, HOW I MADE THIS ###

import stim_handling as stims  #github.com/dbath/fishMAD
import imgstore # pip install imgstore
import joblib
import pandas as pd
import numpy as np
import datetime

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
        df.loc[:,'reversal'] = 0
        df.loc[reversals, 'reversal'] = 1
        df.loc[df['Time'] > 300, 'reversal'] = 0
        df.loc[:,'coh'] = 1.0
        alignPoints = list(df[df['reversal'] == 1]['Timestamp'].values)
        
    else:
        XLIM = (-30,400)
        df.loc[:,'stimStart'] = 0
        firstStim = df.loc[df['Timestamp'] < df['Timestamp'].median(), 'speed'].idxmax()
        df.loc[firstStim, 'stimStart'] = 1
        df.loc[:,'stimEnd'] = 0
        lastStim = df.loc[df['Timestamp'] > df['Timestamp'].median(), 'speed'].idxmin()
        df.loc[lastStim, 'stimEnd'] = 1
        alignPoints = list(df[df['stimStart'] == 1]['Timestamp'].values)

    trials = pd.DataFrame()
    trialID = 0    
    #df = df[df[col].isnull() == False]
    if len(alignPoints) == 0:
        print("found no stim start frames - aborting")
        return 0, pd.DataFrame()
    for i in alignPoints:
        data = df.loc[df['Timestamp'].between(i+XLIM[0], i+XLIM[1]),:].copy()
        for column in data.columns:
            if ('n_dRotation' in column) or ('centroidRotation' in column): #what a silly hack to catch all the different names for rotation. lazy
                data[column] = data[column]*np.sign(data['dir'].mean())
        data['syncTime'] = pd.to_timedelta(data['Timestamp']-i,'s') 
        data['trialID'] = ID + '_' + str(trialID)
        data['date'] = ID.split('_')[0]   
        data['startTime'] = ID.split('_')[1]   
        trialID += 1
        trials = pd.concat([trials, data], axis=0)
    return 1, trials



def save_rotation_data(expFileName):

    if 'reversal' in expFileName:
        REVERSAL=True
        XLIM=(30,60)
        COLUMN='dir'
    else:
        REVERSAL=False
        XLIM=(30,300)
        COLUMN='speed'
    try:
        fbf = pd.read_pickle(expFileName + '/track/perframe_stats.pickle')
        if len(fbf) == 0:
            print("FAILED TO READ PICKLE. TRYING JOBLIB")
            fbf = joblib.load(expFileName + '/track/perframe_stats.pickle')
        rot = pd.read_pickle(expFileName + '/track/rotationOrders_cArea.pickle')
        if not 'frame' in fbf.columns:
            fbf['frame'] = fbf.index
        if not 'FrameNumber' in fbf.columns:
            ret, fbf = stims.sync_data(fbf, 
                          stims.get_logfile(expFileName), 
                          imgstore.new_for_filename(expFileName + '/metadata.yaml')
                          )
        ID = expFileName.split('/')[-1].split('_',3)[-1].split('.')[0]
        ret, synced = sync_by_stimStart(fbf, ID, col=COLUMN,REVERSALS=REVERSAL)     
        if ret == 0:
            return 0
        for IDx in list(set(synced['trialID'])):
            chunk = synced.loc[synced['trialID']==IDx, :]            
            ix = chunk[chunk.syncTime.between(np.timedelta64(XLIM[0], 's'), np.timedelta64(XLIM[1],'s'))].index 
            DIR = np.sign(chunk.loc[ix,'dir'].mean())
            if DIR == 0:
                return 0
            data = np.concatenate([rot[x] for x in range(ix.min(), ix.max())])*DIR*-1.0 #FLIP TO MAKE POSITIVE, JAKE
            COH = str(np.around(fbf.coh.mean(), 1)) 
            GS = expFileName.split('/')[-1].split('_')[1] 
            if REVERSAL:
                np.save('/media/recnodes/Dan_storage/20200121_reversal_rotation_data/' + GS + '_' + COH + '_' + IDx + '.npy', data)
                print('/media/recnodes/Dan_storage/20200121_reversal_rotation_data/' + GS + '_' + COH + '_' + IDx + '.npy' )       
            else:
                continue #FIXME danno's too chicken to try this cuz it'll surely break
                np.save('/media/recnodes/Dan_storage/191205_rotation_data/' + GS + '_' + COH + '_' + ID + '.npy', data)
                print('/media/recnodes/Dan_storage/191205_rotation_data/' + GS + '_' + COH + '_' + ID + '.npy')
        return 1
    except Exception as e:
        print(e)
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
        file_prefix = 'REV_'
        COLUMN='dir'
    else:
        REVERSAL = False
        prestim_frames = 1200
        poststim_frames = 16000
        file_prefix = 'COH_'  
        COLUMN='speed'      
    try:
        fbf = pd.read_pickle(expFileName + '/track/frameByFrameData.pickle')
        if len(fbf.shape) ==1:
            fbf = joblib.load(expFileName + '/track/frameByFrameData.pickle')
        pf = pd.read_pickle(expFileName + '/track/perframe_stats.pickle')#FIXME these may have the wrong stim direction because of sync_data vs sync_coherence (if made before 20191218)....
        if len(pf.shape) ==1:
            pf = joblib.load(expFileName + '/track/perframe_stats.pickle')
        if not 'frame' in pf.columns:
            fbf['frame'] = pf.index
        if not 'FrameNumber' in pf.columns:
            try:
                ret, pf = stims.sync_data(pf, 
                          stims.get_logfile(expFileName), 
                          imgstore.new_for_filename(expFileName + '/metadata.yaml')
                          )    
            except:
                print("oppala")
                return 0    
        ret, sy = sync_by_stimStart(pf,expID, col=COLUMN,REVERSALS=REVERSAL)
        if ret == 0:
            return 0
            
    except Exception as e:
        print(e)
        return 0
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
        stimdir = md['dir'].fillna(0)
        stimcoh = md['coh'].fillna(0)
        stimspeed = md['speed'].fillna(0)
        meta = {}

        COH = str(np.around(pf.coh.median(), 1))
        GS = expFileName.split('/')[-1].split('_')[1]
        #ID = expFileName.split('/')[-1].split('_',3)[-1].split('.')[0]
        FN = '/media/recnodes/Dan_storage/Jake_TS/'+ file_prefix + GS + '_' + COH + '_' + ID + '.npz'
        
        #FN = '/media/recnodes/Dan_storage/Jake_TS/'+ expFileName.split('/')[-1].rsplit('_',2)[0] + '_' + ID + '.npz'
        
        np.savez(FN, rA=rotA, rM=rotM, prestim=psMeta, meta=meta, direction=stimdir,
                     coherence=stimcoh, speed=stimspeed)
        print('completed:', FN)
 
    return  1
    
        
if __name__ == "__main__":
    import glob
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--handle', type=str, required=False, default='', 
                        help='provide unique identifier (or comma-separated list) to select a subset of directories.')


                
    args = parser.parse_args()
    
    #HANDLE = args.handle.split(',')
    filelist = []
    for fn in glob.glob('/media/recnodes/Dan_storage/Jake_TS/*.npz'):
        filelist.append(fn.split('/')[-1].split('_',3)[-1].rsplit('_',1)[0])#FIXME
    #print(filelist)    
    for fn in glob.glob('/media/recnodes/recnode_2mfish/' + args.handle + '*.stitched'):
        ID = fn.split('/')[-1].split('_',3)[-1].split('.')[0]
        #print(ID)
        if ID in filelist: #disabled to re-run
            continue
        ret = save_rotation_data(fn)        
        if not ret:
            print("failed for: ", fn.split('/')[-1])
        ret = get_Tseries(fn)
        if not ret:
            print("tseries failed for ", fn.split('/')[-1])







