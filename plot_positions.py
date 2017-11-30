import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utilities import *
import argparse



def plot_positions(DIR):
    DIR = slashdir(DIR)
    fbf = pd.read_pickle(DIR + 'track/frameByFrameData.pickle')
    ymax, xmax = (2048, 2048)
    my_dpi = 300
    my_figsize = [xmax/my_dpi, ymax/my_dpi]
    fig  = plt.figure(figsize=my_figsize, dpi=my_dpi)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    plt.hist2d(16.0*fbf.dropna()[XPOS].values, 16.0*fbf.dropna()[YPOS].values, bins=256)
    #plt.colorbar()
    plt.savefig(DIR + 'track/positions.svg', bbox_inches='tight',pad_inches = 0)
    plt.savefig(DIR + 'track/positions.png', dpi=my_dpi)#, bbox_inches='tight',pad_inches = 0)
    plt.close('all')
    return
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--v', type=str, required=True,
                        help="path to video's main directory, eg: '/recnode/exp_20170527_162000")
                        
    args = parser.parse_args()
    TRACK_DIR = slashdir(args.v) + 'track/'
    if not os.path.exists(TRACK_DIR + 'frameByFrame_complete' ):
        fbf = getFrameByFrameData(TRACK_DIR)       
    plot_positions(slashdir(args.v))
