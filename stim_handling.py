from __future__ import print_function
import pandas as pd
import numpy as np
import imgstore
from utilities import *



def process_logfile(filename):
    log = pd.read_table(filename)
    log['Timestamp'] = log['Timestamp'] / 1000.0
    log['diff'] = (log['Timestamp'] - log['Timestamp'].shift()).fillna(1000)
    log.loc[log['diff'] < 5, 'Timestamp'] = log['Timestamp'].shift()
    return log.groupby('Timestamp').first().reset_index()
    
def get_coherence(log):    
    log['dotVel'] = log['nDots'] * log['speed']/abs(log['speed']) * log['dir']
    s = log.groupby('Timestamp').sum()
    s['coherence'] = ((s['dotVel'] / s['nDots']) / 2.0) + 0.5  #ranges from 0 to 1
    return s['coherence'].reset_index()
    
def get_speed(log):    
    s = log.groupby('Timestamp').mean()
    return s['speed'].reset_index()

def get_direction(log):    
    s = log.groupby('Timestamp').mean()
    return s['dir'].reset_index()

def synch_coherence_with_rotation(r, log, store):
    """
    pass: r - any df with frame number (0>N) as index
          log - a corresponding log file (from get_logfile())
          store - imgstore object of corresponding video
    returns:  df with frame numbers from camera, timestamps, and stim info
    """    

    foo = get_frame_metadata(r, store)
    
    
    bar = foo.merge(log, how='outer') 
    bar = bar.sort_values('Timestamp') 
    bar['coh'] = bar['coh'].fillna(method='ffill')
    bar['coherence'] = bar['coh']#silly lazy hack
    bar['speed'] = bar['speed'].fillna(method='ffill').fillna(0)
    bar['dir'] = log.loc[0, 'dir'] #first row represents coherent stim dir
    bar.loc[:,'Time'] = (bar.loc[:,'Timestamp'] - bar.loc[0,'Timestamp'])
    if bar.iloc[5].Timestamp - bar.iloc[0].Timestamp > 10: #check if log overlaps with track data
        return 0, bar
    else:    
        return 1, bar  

def correct_timestamps(stitched_store_fn):
    """
    gets timestamps from master machine and transfers them to the stitched store. this is to correct timestamps of videos taken in september 2019 when the slave clock was fast by 338 seconds.
    """
    master_store = imgstore.new_for_filename(stitched_store_fn.rsplit('.',1)[0] + '.21990449/metadata.yaml')
    
    md = pd.DataFrame(master_store.get_frame_metadata())
    
    try:
        for z in glob.glob(stitched_store_fn + '/*.npz'):
            f = np.load(z)
            keys = [key for key in f.files]
            nf = {}
            for name in keys:
                nf[name] = f[name]
            frames = nf['frame_number']
            nf['frame_time'] = [md.loc[(md['frame_number']-i).abs().argsort()[0],'frame_time'] for i in frames]

            np.savez(z.split('.npz')[0], **nf)

        return 1
    except:
        print("FAILED FOR:", stitched_store_fn)
        return 0

def get_logfile(MAIN_DIR):

    MAIN_DIR = slashdir(MAIN_DIR)
    if 'stitch' in MAIN_DIR:
        LOG_FN = '/media/recnodes/Dan_storage/dotbot_logs/dotbotLog_' + MAIN_DIR.split('/')[-2].rsplit('.',1)[0] + '.txt'
    else:
        LOG_FN = '/media/recnodes/Dan_storage/dotbot_logs/dotbotLog_' + MAIN_DIR.split('/')[-2] + '.txt'
    

    log = pd.read_table(LOG_FN)
    log['Timestamp'] = pd.to_numeric(log['Timestamp'], errors='coerce')
    log.loc[:,'Timestamp'] /=  1000.0
    
    return log

def get_frame_metadata(df, store):
    framelist = pd.DataFrame(store.get_frame_metadata())
    framelist.columns=['FrameNumber','Timestamp'] 

    foo = df.merge(framelist, left_on='frame', right_index=True)
    return foo    


def sync_data(r,log,store):
    if '_201909' in store.filename:
        checkname = store.filename.rsplit('.',1)[0] + '.21990449/metadata.yaml'
        check9 = imgstore.new_for_filename(checkname)
        deltaT = check9.get_frame_metadata()['frame_time'][0] - store.get_frame_metadata()['frame_time'][0]
        if abs(deltaT) > 1.0:
            print("**********TIMESTAMP MISMATCH ", str(deltaT), "sec. REPAIRING STORE.********")
            correct_timestamps(store.filename)
            print("*** repair successful ***")
            store = imgstore.new_for_filename(store.filename + '/metadata.yaml')
    foo = get_frame_metadata(r, store)
    bar = foo.merge(log, how='outer') 
    bar = bar.sort_values('Timestamp') 
    bar = bar.fillna(method='ffill')
    if 'speed' in bar.columns:
        bar['speed'] = bar['speed'].fillna(0)
    if 'dir' in bar.columns:
        bar['dir'] = bar['dir'].fillna(0)
    bar.loc[:,'Time'] = (bar.loc[:,'Timestamp'] - bar.loc[0,'Timestamp'])
    if bar.iloc[5].Timestamp - bar.iloc[0].Timestamp > 10: #check if log overlaps with track data
        return 0, bar
    else:    
        return 1, bar  

def sync_reversals(r, log, store):
    """
    pass: r - any df with frame number (0>N) as index
          log - a corresponding log file (from get_logfile())
          store - imgstore object of corresponding video
    returns:  df with frame numbers from camera, timestamps, and stim info
    """    

    foo = get_frame_metadata(r, store)
    
    
    bar = foo.merge(log, how='outer') 
    bar = bar.sort_values('Timestamp') 
    bar['speed'] = bar['speed'].fillna(method='ffill').fillna(0)
    bar['dir'] = bar['dir'].fillna(method='ffill').fillna(0)
    bar.loc[:,'Time'] = (bar.loc[:,'Timestamp'] - bar.loc[0,'Timestamp'])
    if bar.iloc[5].Timestamp - bar.iloc[0].Timestamp > 10: #check if log overlaps with track data
        return 0, bar
    else:    
        return 1, bar  

def synch_reversals(MAIN_DIR, r=None):
    MAIN_DIR = slashdir(MAIN_DIR)
    TRACK_DIR = MAIN_DIR + 'track/'
    LOG_FN = '/media/recnodes/Dan_storage/dotbot_logs/dotbotLog_' + MAIN_DIR.split('/')[-2] + '.txt'
    
    if r == None:
        r = pd.read_pickle(TRACK_DIR + 'frame_means_rotation_polarization.pickle')
    store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml')

    framelist = pd.DataFrame(store.get_frame_metadata())
    framelist.columns=['FrameNumber','Timestamp'] 

    foo = r.merge(framelist, left_index=True, right_index=True)

    log = pd.read_table(LOG_FN)
    log.loc[:,'Timestamp'] /=  1000.0

    bar = foo.merge(log, how='outer') 
    bar = bar.sort_values('Timestamp') 
    bar['speed'] = bar['speed'].fillna(method='ffill').fillna(0)
    bar['dir'] = bar['dir'].fillna(method='ffill').fillna(0)
    bar.loc[:,'Time'] = (bar.loc[:,'Timestamp'] - bar.loc[0,'Timestamp'])
    if bar.iloc[5].Timestamp - bar.iloc[0].Timestamp > 10: #check if log overlaps with track data
        return 0, bar
    else:    
        return 1, bar  

    
def Xsynch_coherence_with_rotation(MAIN_DIR):
    #MAIN_DIR = slashdir('/media/recnodes/kn-crec06/juvenilesfwdmix_3264_dotbot_20171205_101600')
    MAIN_DIR = slashdir(MAIN_DIR)
    TRACK_DIR = MAIN_DIR + 'track/'
    LOG_FN = '/media/recnodes/recnode_jolle2/dotbot_logs/dotbotLog_' + MAIN_DIR.split('/')[-2] + '.txt'

    r = pd.read_pickle(TRACK_DIR + 'frame_means_rotation_polarization.pickle')
    store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml')


    log = process_logfile(LOG_FN)
    coherence = get_coherence(log)
    coherence['speed'] = get_speed(log)['speed']  
    coherence['dir'] = get_direction(log)['dir'] 
    framelist = pd.DataFrame(store.get_frame_metadata())
    framelist.columns=['FrameNumber','Timestamp'] 

    foo = r.merge(framelist, left_index=True, right_index=True)

    bar = foo.merge(coherence, how='outer')
    bar = bar.sort_values('Timestamp')
    bar['coherence'] = log['coh'].mean()#bar['coherence'].fillna(method='ffill')
    bar['speed'] = bar['speed'].fillna(method='ffill').fillna(0)
    bar['dir'] = bar['dir'].fillna(method='ffill').fillna(0)
    bar.loc[:,'Time'] = (bar.loc[:,'Timestamp'] - bar.loc[0,'Timestamp'])

    return bar#.fillna(np.inf)

