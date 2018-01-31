import argparse
import pandas as pd
import numpy as np
from utilities import *
import matplotlib.pyplot as plt
import stim_handling
from pykalman import KalmanFilter



def plot_density(DIR, df, colx, coly, fn=''):
    ymax, xmax = (2048, 2048)
    my_dpi = 300
    my_figsize = [xmax/my_dpi, ymax/my_dpi]
    fig  = plt.figure(figsize=my_figsize, dpi=my_dpi)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    if (colx == 'dRotation') or (coly == 'dRotation'):
        ax.set_ylim(-1,1)
    else:
        ax.set_ylim(0,1)
    cmap=plt.cm.jet
    cmap.set_bad(color='black')
    cmap.set_under(color='black')
    plt.hist2d(df.dropna()[colx].values, df.dropna()[coly].values, bins=256, cmap=cmap, vmin=0.0000000001)
    #plt.colorbar()
    plt.savefig(DIR + 'track/density_'+fn + colx + '-x_' + coly + '-y.svg', bbox_inches='tight',pad_inches = 0)
    plt.savefig(DIR + 'track/density_'+fn + colx + '-x_' + coly + '-y.png', dpi=my_dpi)#, bbox_inches='tight',pad_inches = 0)
    plt.close('all')
    return
    
def get_centroid(arr):
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    return sum_x/length, sum_y/length

def get_colours(L):
    """pass an integer (L), returns a list of length (L) with colour codes"""
    foo = cm.hsv(np.linspace(0, 1, L))
    np.random.shuffle(foo)
    return foo

def doit(fbf, TRACK_DIR):
    f = fbf.groupby(['frame'])
    frame_means = pd.DataFrame()
    frame_stds = pd.DataFrame()

    for i, data in f:
        data = data.dropna().copy()

        #polarity
        
        data.loc[:,'speed'] = np.sqrt(data.loc[:,XVEL]**2 + data.loc[:,YVEL]**2)
        data.loc[:,'uVX'] = data.loc[:,XVEL] / data.loc[:,'speed'] # X component of unit vector
        data.loc[:,'uVY'] = data.loc[:,YVEL] / data.loc[:,'speed'] # Y component of unit vector
        
        #polarization is the length of the average of all unit vectors
        polarization = abs(np.sqrt((data.loc[:,'uVX'].mean())**2 + (data.loc[:,'uVY'].mean())**2))
        
        
        #angular momentum of fish
        points = np.array(zip(data.loc[:,XPOS], data.loc[:,YPOS]))
        centroid = get_centroid(points)   
        
        data.loc[:,'CX'] = data.loc[:,XPOS] - centroid[0] # component vector to centroid, X
        data.loc[:,'CY'] = data.loc[:,YPOS] - centroid[1] # component vector to centroid, Y
        data.loc[:,'radius'] = np.sqrt(data.loc[:,'CX']**2 + data.loc[:,'CY']**2)  #radius to centroid
        data.loc[:,'uCX'] = data.loc[:,'CX'] / data.loc[:,'radius'] # X component of unit vector R
        data.loc[:,'uCY'] = data.loc[:,'CY'] / data.loc[:,'radius'] # Y component of unit vector R
        data = data.dropna()
        
        rotation_directed = np.cross(data[['uCX','uCY']], data[['uVX','uVY']])
        rotation = abs(rotation_directed)
        rotation = rotation[~np.isnan(rotation)]

        
        frame_means.loc[i, 'cx'] = centroid[0]
        frame_means.loc[i, 'cy'] = centroid[1]
        frame_means.loc[i, 'radius'] = data['radius'].mean()
        frame_means.loc[i, 'polarization'] = abs(np.sqrt((data['uVX'].mean())**2 + (data['uVY'].mean())**2))
        frame_means.loc[i, 'rotation'] = rotation.mean()
        frame_means.loc[i, 'dRotation'] = rotation_directed.mean()
        
        frame_stds.loc[i, 'radius'] = data['radius'].std()
        frame_stds.loc[i, 'polarization'] = abs(np.sqrt((data['uVX'].std())**2 + (data['uVY'].std())**2))
        frame_stds.loc[i, 'rotation'] = rotation.std()
        frame_stds.loc[i, 'dRotation'] = rotation_directed.std()
        
        
    frame_means.to_pickle(TRACK_DIR + '/frame_means_rotation_polarization.pickle')
    frame_stds.to_pickle(TRACK_DIR + '/frame_stds_rotation_polarization.pickle')
    return frame_means, frame_stds

def kalman(df):
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

    kf1 = kf1.em(measurements, n_iter=10)
    (smoothed_state_means, smoothed_state_covariances) = kf1.smooth(measurements)
    return smoothed_state_means[:,1], smoothed_state_means[:,3]


def get_centroid_rotation(_MAIN_DIR, df):
    #GET UNIT VECTORS OF GROUP CENTROID VELOCITY
    """
    df['vx'] = df['cx'] - df.shift()['cx']
    df['vy'] = df['cy'] - df.shift()['cy']
    df['speed'] = np.sqrt(df['vx']**2 + df['vy']**2)
    """

    df['vx'], df['vy'] = kalman(df)
    df['speed'] = np.sqrt(df['vx']**2 + df['vy']**2)
    df['uVX'] = df['vx'] / df['speed'] # X component of unit vector
    df['uVY'] = df['vy'] / df['speed'] # Y component of unit vector
    
    #GET WIDTH OF ARENA TO DEFINE CENTRE
    conv = open(_MAIN_DIR + 'track/conversion.settings')
    SETTINGS = conv.readlines()
    for item in SETTINGS:
        if item.find('real_width') !=-1:
             ARENA_WIDTH = int(item.split(' = ')[1].split('\n')[0]  )
    conv.close()
    
    #GET UNIT VECTORS OF GROUP CENTROID POSITION
    df['CX'] = df['cx'] - (ARENA_WIDTH/2.0)
    df['CY'] = df['cy'] - (ARENA_WIDTH/2.0)
    df['radius'] = np.sqrt(df['CX']**2 + df['CY']**2)  #radius to centroid
    df['uCX'] = df['CX'] / df['radius'] # X component of unit vector R
    df['uCY'] = df['CY'] / df['radius'] # Y component of unit vector R

    #GET ROTATION ORDER:
    df['centroid_rotation_directed'] = np.cross(df[['uCX','uCY']], df[['uVX','uVY']])
    df['centroid_rotation'] = abs(df['centroid_rotation_directed'])
    
    
    #FIXME incomplete function
    
    return


def plot_order_vs_time(DIR, colA, colB, fn=''):
    df = pd.read_pickle(DIR + 'track/frame_means_rotation_polarization.pickle')
    if not 'coherence' in df.columns:
        df = stim_handling.synch_coherence_with_rotation(DIR)
    df = df[df['FrameNumber'].notnull()]
    fig  = plt.figure()
    fig.suptitle(DIR.split('/')[-2])
    subs = ['coherence',colA, colB]
    colourlist = ['black','red','blue']
    ylabs = ['% Clockwise','Order','Order']
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312, sharex=ax1)
    ax3 = fig.add_subplot(313, sharex=ax1)
    axes = [ax1, ax2, ax3]
    for REP in range(len(subs)):
        ax = axes[REP]
        fig.add_axes(ax)
        plt.plot(df.Time, df[subs[REP]].values, color=colourlist[REP])
        ax.set_title(subs[REP])
        ax.set_ylabel(ylabs[REP])
        if REP <2:
            plt.setp(ax.get_xticklabels(), visible=False)
        else:
            ax.set_xlabel('Time (s)')
        if subs[REP] == 'dRotation':
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
    plt.savefig(DIR + 'track/vsTime_'+fn + colA + '_' + colB + '.svg', bbox_inches='tight',pad_inches = 0)
    plt.savefig(DIR + 'track/vsTime_'+fn + colA + '_' + colB + '.png')#, bbox_inches='tight',pad_inches = 0)
    plt.close('all')
    return

def run(DIR):
    TRACK_DIR = slashdir(DIR) + 'track/'
    if not os.path.exists(TRACK_DIR + 'frameByFrame_complete' ):
        _fbf = getFrameByFrameData(TRACK_DIR)       
    else:
        _fbf = pd.read_pickle(TRACK_DIR + 'frameByFrameData.pickle')
                
    if not os.path.exists(TRACK_DIR + 'frame_means_rotation_polarization.pickle'):
        print "calculating rotation and polarization"
        frame_means, frame_stds = doit(_fbf, TRACK_DIR)
    else:
        frame_means = pd.read_pickle(TRACK_DIR + 'frame_means_rotation_polarization.pickle')
        if not 'dir' in frame_means.columns:
            frame_means, frame_stds = doit(_fbf, TRACK_DIR)
        else:
            frame_stds = pd.read_pickle(TRACK_DIR + 'frame_stds_rotation_polarization.pickle')
    
    plot_density(slashdir(DIR), frame_means, 'rotation','polarization', 'mean')
    plot_density(slashdir(DIR), frame_means, 'dRotation','polarization', 'mean')
    plot_density(slashdir(DIR), frame_stds, 'rotation','polarization', 'std') 
    plot_order_vs_time(slashdir(DIR),  'rotation','polarization')  
    plot_order_vs_time(slashdir(DIR),  'dRotation','polarization')  
    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--v', type=str, required=True,
                        help="path to video's main directory, eg: '/recnode/exp_20170527_162000")
                        
    args = parser.parse_args()
    TRACK_DIR = slashdir(args.v) + 'track/'
    run(slashdir(args.v))
    
    
    
