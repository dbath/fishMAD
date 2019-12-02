

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

def crop_stitched_img(img):
    if len(img.shape)==2:
        h,w = img.shape
        return img[100:h-100,100:w-100]
    elif len(img.shape)==3:
        h, w, _ = img.shape
        return img[100:h-100,100:w-100,:]


XPOS = 'X#wcentroid'
YPOS = 'Y#wcentroid'
XVEL = 'VX#smooth#wcentroid'
YVEL = 'VY#smooth#wcentroid'
SPEED = 'SPEED#smooth#wcentroid'
ACC = 'ACCELERATION#smooth#wcentroid'
angVel = 'ANGULAR_A#wcentroid'
angAcc = 'ANGULAR_V#wcentroid'




def plot_data_on_video(img, xdata, ydata, colourdata, stimdata, fig=None, ax=None,
                        xlim=(7,312), ylim=(8,327),_alpha=1.0,
                        colourNorm='undefined'):
    if fig==None:
        fig = plt.figure(frameon=False)
        fig.set_size_inches(4,4)
    if ax== None:
        ax = fig.add_subplot(111)
    plt.imshow(crop_stitched_img(img), extent=[xlim[0], xlim[1],ylim[0],ylim[1]], origin='lower')
    
    if stimdata > 0.5:
        TEXT = 'Clockwise'
        props = dict(boxstyle='round', facecolor='#4a8a49', alpha=0.5)
    elif stimdata < -0.5:
        TEXT = 'Counter clockwise'
        props = dict(boxstyle='round', facecolor='#eb2d02', alpha=0.5)
    else:
        TEXT = 'No Stimulus'
        props = dict(boxstyle='round', facecolor='#ffffff', alpha=0.5)
    ax.text(0.97, 0.02, TEXT, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right', bbox=props)
    
    #normalize colour data
    if colourNorm=='undefined':
        VMIN = colourdata.min()
        VMAX = colourdata.max()
    else:
        VMIN, VMAX = colourNorm
    
    data = plt.scatter(xdata, ydata, c=colourdata, s=3, alpha=_alpha, vmin=VMIN, vmax=VMAX) 
    
    plt.gca().set_aspect(1.0)
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
            hspace = 0, wspace = 0)    
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    
    return fig
    

if __name__ == "__main__":
    import joblib
    import stim_handling as stims
    import imgstore
    import os
    import pandas as pd
    import numpy as np
    
    MAIN_DIR = '/media/recnodes/recnode_2mfish/reversals3m_64_dotbot_20181024_153201.stitched/'
    
    DATA_COL = 'EigenCen'
    STIM_COL = 'dir'
    SKIP_FRAMES=3
    
    SAVE_DIR = MAIN_DIR + 'track/eigencentricity_overlay/'
    
    nfbf = joblib.load(MAIN_DIR + 'track/network_FBF.pickle')
    nfbf.index = nfbf.frame
    store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml')
    log = stims.get_logfile(MAIN_DIR)
    ret, pf = stims.sync_data(pd.read_pickle(MAIN_DIR + 'track/perframe_stats.pickle'), log, store)
    
    ret, nfbf = stims.sync_data(nfbf, log, store)
    
    
    frames = pd.DataFrame(store.get_frame_metadata()) 
    frames.columns = ['FrameNumber','Timestamp']  
    
    _MIN = nfbf[DATA_COL].min()
    _MAX = nfbf[DATA_COL].max()
    
    g = nfbf.groupby('frame')
    
    for i in np.arange(0,len(frames), SKIP_FRAMES):
        if os.path.exists(SAVE_DIR + '%06d.png'%i):
            continue
        print(i)
        f = frames.loc[i, 'FrameNumber']
        img, (md) = store.get_image(f)
        data = g.get_group(i)
        fig = plot_data_on_video(img, data[XPOS], data[YPOS], data[DATA_COL], data[STIM_COL].median(), 
                                 colourNorm=(_MIN,_MAX))
        plt.savefig(SAVE_DIR + '%06d.png'%i)
        plt.close('all')
