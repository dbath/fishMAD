import argparse
import pandas as pd
import numpy as np
from utilities import *
import matplotlib.pyplot as plt



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
        data = data.dropna()

        #polarity
        
        data['speed'] = np.sqrt(data[XVEL]**2 + data[YVEL]**2)
        data['uVX'] = data[XVEL] / data['speed'] # X component of unit vector
        data['uVY'] = data[YVEL] / data['speed'] # Y component of unit vector
        
        #polarization is the length of the average of all unit vectors
        polarization = abs(np.sqrt((data['uVX'].mean())**2 + (data['uVY'].mean())**2))
        
        
        #angular momentum of fish
        points = np.array(zip(data[XPOS], data[YPOS]))
        centroid = get_centroid(points)   
        
        data['CX'] = data[XPOS] - centroid[0] # component vector to centroid, X
        data['CY'] = data[YPOS] - centroid[1] # component vector to centroid, Y
        data['radius'] = np.sqrt(data['CX']**2 + data['CY']**2)  #radius to centroid
        data['uCX'] = data['CX'] / data['radius'] # X component of unit vector R
        data['uCY'] = data['CY'] / data['radius'] # Y component of unit vector R
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

def plot_order_vs_time(DIR, df, colA, colB, fn=''):
    fig  = plt.figure()
    ax = fig.add_subplot(111)#plt.Axes(fig, [0., 0., 1., 1.])
    fig.add_axes(ax)
    plt.plot(df.dropna()[colA].values, color='red', label=colA)
    plt.plot(df.dropna()[colB].values, color='blue', label=colB)
    ax.set_xlabel('Frame')
    ax.set_ylabel('Order')
    if (colA == 'dRotation') or (colB == 'dRotation'):
        ax.set_ylim(-1,1)
        ax.set_yticks([-1,0,1])
    else:
        ax.set_ylim(0,1) 
        ax.set_yticks([0,0.5,1])
    ax.legend(loc=0)
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
                
    if not os.path.exists(TRACK_DIR + '/frame_means_rotation_polarization.pickle'):
        print "calculating rotation and polarization"
        frame_means, frame_stds = doit(_fbf, TRACK_DIR)
    else:
        frame_means = pd.read_pickle(TRACK_DIR + '/frame_means_rotation_polarization.pickle')
        frame_stds = pd.read_pickle(TRACK_DIR + '/frame_stds_rotation_polarization.pickle')
    
    plot_density(slashdir(DIR), frame_means, 'rotation','polarization', 'mean')
    plot_density(slashdir(DIR), frame_means, 'dRotation','polarization', 'mean')
    plot_density(slashdir(DIR), frame_stds, 'rotation','polarization', 'std') 
    plot_order_vs_time(slashdir(DIR), frame_means, 'rotation','polarization')  
    plot_order_vs_time(slashdir(DIR), frame_means, 'dRotation','polarization')  
    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--v', type=str, required=True,
                        help="path to video's main directory, eg: '/recnode/exp_20170527_162000")
                        
    args = parser.parse_args()
    run(slashdir(args.v))
    TRACK_DIR = slashdir(DIR) + 'track/'
    
    
    
