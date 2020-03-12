import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.gridspec as gridspec
from skimage import exposure

def get_frameset(pfchunk, starttime):
    framelist = []
    start = pfchunk.loc[pfchunk.Time.between(starttime+1.0, starttime+1.5)]
    DIR = np.sign(start.loc[np.argmin(np.abs(start['median_dRotation_cArea'])-1.0), 'median_dRotation_cArea'])
    framelist.append(start.loc[np.argmin(np.abs(start['median_dRotation_cArea'])-1.0), 'FrameNumber'])
    #framelist.append(pfchunk.loc[np.argmin(np.abs(pfchunk['Time']-starttime)), 'FrameNumber'])
    for r in [0.75,0.5,0,-0.5,-0.75, -0.9, -1.0]:
        framelist.append(pfchunk.loc[np.argmin(np.abs(pfchunk['median_dRotation_cArea']-r*DIR)),'FrameNumber'])

    return framelist
    
    
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

def plot_data_on_video(img, xdata, ydata, colourdata, TEXT, fig=None, ax=None,
                        xlim=(7,312), ylim=(8,327)):
    if fig==None:
        fig = plt.figure(frameon=False)
        fig.set_size_inches(4,4)
    if ax== None:
        ax = fig.add_subplot(111)
    plt.imshow(crop_stitched_img(img), extent=[xlim[0], xlim[1],ylim[0],ylim[1]], origin='lower')
    
    
    props = dict(boxstyle='round', facecolor='#ffffff', alpha=0.75)
    ax.text(0.97, 0.02, TEXT, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right', bbox=props)
    

    
    data = plt.scatter(xdata, ydata, c=colourdata, s=0.25) 
    
    plt.gca().set_aspect(1.0)
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
            hspace = 0, wspace = 0)    
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    
    return fig
    
def create_colourlist(N, cmap='viridis', rev=False):
    import matplotlib.pyplot as plt
    if rev ==True:
        return plt.cm.get_cmap(cmap)(np.linspace(1,0,N))
    else:    
        return plt.cm.get_cmap(cmap)(np.linspace(0,1,N))


def plotnice(plotType='standard', ax=plt.gca()):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if plotType == 'hist':
        ax.spines['left'].set_visible(False)
        ax.set_yticks([])
    elif plotType=='img':
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        plt.axis('off')
    return

if __name__ == "__main__":
    import argparse
    from utilities import *
    import stim_handling as stims
    import imgstore
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=True, help='path to main directory')
    parser.add_argument('--time', type=float, required=True, 
                        help='provide a time in seconds, eg 280.9')


                
    args = parser.parse_args()
    
    MAIN_DIR = slashdir(args.dir)

    
    store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml')
    log = stims.get_logfile(MAIN_DIR)

    print('loading pf')
    pf = pd.read_pickle(MAIN_DIR + 'track/perframe_stats.pickle')
    
    if len(pf.shape) ==1:
        import joblib
        pf = joblib.load(MAIN_DIR + 'track/perframe_stats.pickle')
    if not 'frame' in pf.columns:
        pf['frame'] = pf.index
    if not 'FrameNumber' in pf.columns:
        ret, pf = stims.sync_data(pf, log, store)

    T0 = pf.loc[np.argmin(abs(pf.loc[abs(pf.dir - pf.dir.shift()) ==2, 'Time'] - args.time)),'Time'] 

    print('loading fbf')
    fbf = pd.read_pickle(MAIN_DIR + 'track/frameByFrameData.pickle')
    if len(fbf.shape) ==1:
        import joblib
        fbf = joblib.load(MAIN_DIR + 'track/frameByFrameData.pickle')
    if not 'frame' in fbf.columns:
        fbf['frame'] = fbf.index
    if not 'FrameNumber' in fbf.columns:
        print('merging framenumber')
        fbf = fbf.merge(pf[['FrameNumber','frame']], left_on='frame', right_on='frame')
        #ret, fbf = stims.sync_data(fbf, log, store)

    fbf.loc[:,'uVX'] = fbf.loc[:,XVEL] / fbf.loc[:,SPEED]
    fbf.loc[:,'uVY'] = fbf.loc[:,YVEL] / fbf.loc[:,SPEED]
    fbf['R'] = rotationOrder(160,160,fbf[XPOS],fbf[YPOS],fbf['uVX'],fbf['uVY'])
    fbf['colVal'] = fbf['R']/2.0 +0.5 #rescale to 0-1
    
    
    rpf = pf.loc[pf['Time'].between(T0, T0+45),:]
    framelist = get_frameset(rpf, T0)
    rfbf = fbf.loc[fbf['time'].between(T0, T0+45),:]
    cl = create_colourlist(len(set(fbf.trackid)), cmap='viridis')
    cl[:,3] = 0.5 #set alpha
    colours = dict(zip(list(set(fbf.trackid)), cl ))

    N = len(framelist)
    if N <=3:
        gridsize=(1,N)
    elif N <=10:
        gridsize=(2,int(N/2 + N%2))
    elif N <=18:
        gridsize=(3,int(N/3 + N%3))
    #gridsize = (int(N**0.5), N/int(N**0.5) + N%(int(N**0.5)))

    fig = plt.figure(figsize=(gridsize[1]*4, gridsize[0]*4))
    gs1 = gridspec.GridSpec(gridsize[0], gridsize[1])
    gs1.update(wspace=0.025, hspace=0.025)
        
    for i in range(N):
        frame = framelist[i]
        ax = fig.add_subplot(gs1[i])
        try:
            img, (f, t) = store.get_image(frame)
        except:
            img, (f, t) = store.get_next_image()
        
        img = exposure.adjust_sigmoid(img, 0.40, 8)
        
        #ax.imshow(img, cmap='gray', origin=flipped[i])
        #plotnice('img')
        #ax.set_aspect('equal')

        TEXT = str(np.around(rfbf.loc[rfbf['FrameNumber'] ==frame, 'time'].min() -T0,1)) + ' s'
        plotdata = rfbf.loc[rfbf['FrameNumber'].between(frame-40, frame), :]
        
        #plotdata = drop_bad_tracks(plotdata)
        #plotdata = plotdata.loc[(plotdata['SPEED#smooth#wcentroid'] >= 0.1) & (plotdata['BORDER_DISTANCE#wcentroid'] > 20), :] 
        #COLOURS = np.array([colours[x] for x in plotdata.trackid.values])
        COLOURS = plt.cm.get_cmap('viridis')(plotdata['colVal'])
        COLOURS[:,3] = plotdata['time'] - plotdata['time'].min()

        fig = plot_data_on_video(img, plotdata[XPOS], plotdata[YPOS], 
                            COLOURS, 
                            TEXT, fig=fig, ax=ax,
                            xlim=(7,312), ylim=(8,327))    

        props = dict(boxstyle='round', facecolor='#ffffff', alpha=0.75)
        TEXT = 'r= ' + str(np.around(rpf.loc[rpf['FrameNumber']==frame, 'median_dRotation_cArea'].values[0],2))
        ax.text(0.02, 0.02, TEXT, transform=ax.transAxes, fontsize=10,
                verticalalignment='bottom', horizontalalignment='left', bbox=props)
                
                
    plotnice('img')
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
    #plt.show() #FIXME
    plt.savefig(MAIN_DIR + 'track/storyboard_'+str(int(args.time)) + '.png', dpi=200)
    plt.savefig(MAIN_DIR + 'track/storyboard_'+str(int(args.time)) + '.svg', dpi=200)
    plt.close('all')
