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
    
def synch_coherence_with_rotation(MAIN_DIR):
    #MAIN_DIR = slashdir('/media/recnodes/kn-crec06/juvenilesfwdmix_3264_dotbot_20171205_101600')
    MAIN_DIR = slashdir(MAIN_DIR)
    TRACK_DIR = MAIN_DIR + 'track/'
    LOG_FN = '/media/recnodes/recnode_jolle2/dotbot_logs/dotbotLog_' + MAIN_DIR.split('/')[-2] + '.txt'

    r = pd.read_pickle(TRACK_DIR + 'frame_means_rotation_polarization.pickle')
    store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml')


    log = process_logfile(LOG_FN)
    coherence = get_coherence(log)
    coherence['speed'] = get_speed(log)['speed']   
    framelist = pd.DataFrame(store.get_frame_metadata())
    framelist.columns=['FrameNumber','Timestamp'] 

    foo = r.merge(framelist, left_index=True, right_index=True)

    bar = foo.merge(coherence, how='outer')
    bar = bar.sort_values('Timestamp')
    bar['coherence'] = bar['coherence'].fillna(method='ffill')
    bar['speed'] = bar['speed'].fillna(method='ffill').fillna(0)
    bar.loc[:,'Time'] = (bar.loc[:,'Timestamp'] - bar.loc[0,'Timestamp'])

    return bar#.fillna(np.inf)

