import argparse
import pandas as pd
import numpy as np
from utilities import *
import matplotlib.pyplot as plt
import stim_handling
from pykalman import KalmanFilter



def get_centroid(arr):
    try:
        length = arr.shape[0]
        sum_x = np.sum(arr[:, 0])
        sum_y = np.sum(arr[:, 1])
        return sum_x/length, sum_y/length
    except:
        return (np.nan, np.nan)

def get_colours(L):
    """pass an integer (L), returns a list of length (L) with colour codes"""
    foo = cm.hsv(np.linspace(0, 1, L))
    np.random.shuffle(foo)
    return foo


def kalman(df, N_ITER):
    measurements = np.asarray(list(zip(df['cx'], df['cy'])))
    initial_state_mean = [measurements[0, 0],
                          0,
                          measurements[0, 1],
                          0]

    transition_matrix = [[1, 1, 0, 0],
                         [0, 1, 0, 0],
                         [0, 0, 1, 1],
                         [0, 0, 0, 1]]

    observation_matrix = [[1, 0, 0, 0],
                          [0, 0, 1, 0]]

    kf1 = KalmanFilter(transition_matrices = transition_matrix,
                      observation_matrices = observation_matrix,
                      initial_state_mean = initial_state_mean)

    kf1 = kf1.em(measurements, n_iter=N_ITER)
    (smoothed_state_means, smoothed_state_covariances) = kf1.smooth(measurements)
    return smoothed_state_means[:,0], smoothed_state_means[:,2]


def get_centroid_rotation(_MAIN_DIR, df, N_ITER):
    #GET UNIT VECTORS OF GROUP CENTROID VELOCITY
    """
    """
    df = df.loc[df.cx.notnull(), :]
    df = df.loc[df.cy.notnull(), :]
    df['cxK'], df['cyK'] = kalman(df[['cx','cy']], N_ITER) #smooth positions before calculating velocity.
    df['vx'] = df['cxK'] - df.shift()['cxK'] #calculate velocity
    df['vy'] = df['cyK'] - df.shift()['cyK'] #calculate velocity
    df = df.loc[df.vx.notnull(), :]
    df = df.loc[df.vy.notnull(), :]
    
    df['speed'] = np.sqrt(df['vx']**2 + df['vy']**2)
    df['uVX'] = df['vx'] / df['speed'] # X component of unit vector
    df['uVY'] = df['vy'] / df['speed'] # Y component of unit vector
    
    #GET WIDTH OF ARENA TO DEFINE CENTRE
    conv = open(slashdir(_MAIN_DIR) + 'track/conversion.settings')
    SETTINGS = conv.readlines()
    for item in SETTINGS:
        if item.find('real_width') !=-1:
             ARENA_WIDTH = int(item.split(' = ')[1].split('\n')[0]  )
    conv.close()
    
    #GET UNIT VECTORS OF GROUP CENTROID POSITION
    df['CX'] = df['cx'] - (ARENA_WIDTH/2.0)
    df['CY'] = df['cy'] - (ARENA_WIDTH/2.0)
    df['radius'] = np.sqrt(df['CX']**2 + df['CY']**2)  #radius to centre of arena
    df['uCX'] = df['CX'] / df['radius'] # X component of unit vector R
    df['uCY'] = df['CY'] / df['radius'] # Y component of unit vector R

    #GET ROTATION ORDER:
    df['centroid_rotation_directed'] = np.cross(df[['uCX','uCY']], df[['uVX','uVY']])
    df['centroid_rotation'] = abs(df['centroid_rotation_directed'])
    
    
    return df['centroid_rotation_directed']

def stateDependentRotationOrder(df):
    for state in ['milling','swarm','polarized']:
        df.loc[:,state] = 0
    df.loc[(df.polarization < 0.5) & (abs(df.dRotation) >= 0.6), 'milling'] = 1
    df.loc[(df.polarization < 0.3) & (abs(df.dRotation) < 0.65), 'swarm'] = 1
    df.loc[(df.polarization >= 0.5) & (abs(df.dRotation) < 0.60), 'polarized'] = 1
    df.loc[:,'sDRO'] = np.nan
    df.loc[df['milling']==1, 'sDRO'] = df.loc[df['milling']==1, 'dRotation']
    df.loc[df['polarized']==1, 'sDRO'] = df.loc[df['polarized']==1, 'cRotation']
    return df['sDRO']
    
def plot_order_vs_time(DIR,  colA, colB, colC, df=pd.DataFrame(), fn=''):
    if len(df) < 1:
        df = pd.read_pickle(DIR + 'track/frame_means_rotation_polarization.pickle')
    if not 'coherence' in df.columns:
        df = stim_handling.synch_coherence_with_rotation(DIR)
    df = df[df['FrameNumber'].notnull()]
    fig  = plt.figure()
    fig.suptitle(DIR.split('/')[-2])
    subs = ['coherence',colA, colB, colC]
    colourlist = ['black','red','orange','blue']
    ylabs = ['% Clockwise','Order','Order','Order']
    ax1 = fig.add_subplot(411)
    ax2 = fig.add_subplot(412, sharex=ax1)
    ax3 = fig.add_subplot(413, sharex=ax1)
    ax4 = fig.add_subplot(414, sharex=ax1)
    axes = [ax1, ax2, ax3, ax4]
    for REP in range(len(subs)):
        ax = axes[REP]
        fig.add_axes(ax)
        plt.plot(df.Time, df[subs[REP]].values, color=colourlist[REP])
        ax.set_title(subs[REP], y=0.75)
        ax.set_ylabel(ylabs[REP])
        if REP <2:
            plt.setp(ax.get_xticklabels(), visible=False)
        else:
            ax.set_xlabel('Time (s)')
        if 'Rot' in subs[REP]:
            ax.set_ylim(-1,1)
            ax.set_yticks([-1,0,1])
            plt.axhline(y=0.0, color='k', linestyle='-')
        elif subs[REP] == 'coherence':
            ax.set_ylim(-0.1,1.1) 
            ax.set_yticks([0,0.5,1])
            axR = ax.twinx()
            plt.plot(df['Time'], df['speed']*df['dir']*1000.0, color='r')
            axR.set_ylabel('speed', color='r')
            axR.tick_params('y', colors='r')
            axR.set_ylim(-110,110)
            axR.set_yticks([-100,0,100])
        else:
            ax.set_ylim(0,1) 
            ax.set_yticks([0,0.5,1])
    #ax.legend(loc=0)
    #plt.colorbar()
    plt.tight_layout()
    plt.subplots_adjust(hspace=0)
    plt.savefig(DIR + 'track/vsTime_'+fn + colA + '_' + colB + '_' + colC + '.svg', bbox_inches='tight',pad_inches = 0)
    plt.savefig(DIR + 'track/vsTime_'+fn + colA + '_' + colB + '_' + colC + '.png')#, bbox_inches='tight',pad_inches = 0)
    plt.close('all')
    return

def run(DIR):
    TRACK_DIR = slashdir(DIR) + 'track/'
    frame_means = pd.read_pickle(TRACK_DIR + 'frame_means_rotation_polarization.pickle')

    #if not 'coherence' in frame_means.columns:
    frame_means = stim_handling.synch_coherence_with_rotation(DIR)
    
    frame_means['timedelta'] = pd.to_timedelta(frame_means['Time'], unit='s')
    frame_means.index = frame_means['timedelta']
    frame_means = frame_means.resample('1s').median()

    frame_means['cRotation'] = get_centroid_rotation(DIR, frame_means, 10) 
    frame_means['stateDepRotOrder'] = stateDependentRotationOrder(frame_means)
    frame_means.to_pickle(TRACK_DIR + 'centroid_rotation.pickle')
    plot_order_vs_time(slashdir(DIR),   'dRotation','cRotation', 'stateDepRotOrder', df=frame_means)  
    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--v', type=str, required=True,
                        help="path to video's main directory, eg: '/recnode/exp_20170527_162000")
                        
    args = parser.parse_args()
    TRACK_DIR = slashdir(args.v) + 'track/'
    run(slashdir(args.v))
    
    
