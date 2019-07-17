
import imgstore
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from utilities import *
import stim_handling as stims
from skimage import exposure


up40 = ['/media/recnodes/kn-crec05/coherencetestangular_8_dotbot_20180313_123400',
        '/media/recnodes/kn-crec07/coherencetestangular_16_dotbot_20180220_105700',
        '/media/recnodes/kn-crec06/coherencetestangular_32_dotbot_20180220_113600',
        '/media/recnodes/kn-crec06/coherencetestangular_64_dotbot_20180212_115500',
        '/media/recnodes/kn-crec06/coherencetestangular_128_dotbot_20180404_125500', #need to flip
        '/media/recnodes/recnode_2mfish/coherencetestangular3m_64_dotbot_20181023_143201.stitched',
        '/media/recnodes/recnode_2mfish/coherencetestangular3m_128_dotbot_20181211_105201.stitched',
        '/media/recnodes/recnode_2mfish/coherencetestangular3m_256_dotbot_20181214_095202.stitched', #need to flip
        '/media/recnodes/recnode_2mfish/coherencetestangular3m_512_dotbot_20181017_143202.stitched',
        '/media/recnodes/recnode_2mfish/coherencetestangular3m_1024_dotbot_20190201_113201.stitched']
        

up128 = ['/media/recnodes/recnode_2mfish/coherencetestangular3m_128_dotbot_20181008_173202.stitched',  #0    
         '/media/recnodes/recnode_2mfish/coherencetestangular3m_128_dotbot_20181008_125201.stitched',  #20      
         '/media/recnodes/recnode_2mfish/coherencetestangular3m_128_dotbot_20181004_125201.stitched',  #40      
         '/media/recnodes/recnode_2mfish/coherencetestangular3m_128_dotbot_20181004_153201.stitched',  #60        
         '/media/recnodes/recnode_2mfish/coherencetestangular3m_128_dotbot_20181004_141201.stitched',   #80     
         '/media/recnodes/recnode_2mfish/coherencetestangular3m_128_dotbot_20181008_105201.stitched']   #100   


revgs = ['reversals3m_64_dotbot_20181023_111201.stitched',
         'reversals3m_128_dotbot_20181105_111202.stitched',
         'reversals3m_256_dotbot_20181012_101201.stitched',
         'reversals3m_512_dotbot_20181017_121201.stitched',
         'reversals3m_1024_dotbot_20181205_143201.stitched']


def sync_by_stimStart(df, col='speed'):
    """
    pass a df with stim information
    returns the df with rotation values adjusted for direction so rotation of new stim is positive
    """
    df = df.sort_values('FrameNumber').reset_index(drop=True)
    df = df[:-10] #drop end to avoid dealing with annoying NaN cases #lazy #FIXME
    
    df.loc[:,'stimStart'] = 0
    firstStim = df.loc[df['Time'] < df['Time'].median(), 'speed'].idxmax()
    df.loc[firstStim, 'stimStart'] = 1
    df.loc[:,'stimEnd'] = 0
    lastStim = df.loc[df['Time'] > df['Time'].median(), 'speed'].idxmin()
    df.loc[lastStim, 'stimEnd'] = 1
    return df




def sync_by_reversal(df, col='dir', X=20000):
    """
    pass a df with stim information
    returns the df with rotation values adjusted for direction so rotation of new stim is positive
    """
    df = df.sort_values('FrameNumber').reset_index(drop=True)
    df = df[df.index < X]
    df['reversal'] = 0
    reversals = df[abs(df[col] - df.shift()[col]) ==2].index
    df.loc[reversals, 'reversal'] = 1
    df.loc[df['Time'] > 300, 'reversal'] = 0 #FIXME this is a hack solution to sort out ends
    df.loc[df['Time'] < 80, 'reversal'] = 0 #FIXME this is a hack solution to sort out ends
    df['firstStim'] = 0
    firstStim = df[df['Time'] < df['Time'].median()]
    firstStim = firstStim[abs(firstStim[col] - firstStim.shift()[col]) ==1].index
    df.loc[firstStim, 'firstStim'] = 1
    df['lastStim'] = 0
    lastStim = df[df['Time'] > df['Time'].median()]
    lastStim = lastStim[abs(lastStim[col] - lastStim.shift()[col]) ==1].index
    df.loc[lastStim, 'lastStim'] = 1
    return df





def plotnice(plotType='standard'):
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    if plotType == 'hist':
        plt.gca().spines['left'].set_visible(False)
        plt.gca().set_yticks([])
    elif plotType=='img':
        plt.gca().spines['left'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)
        plt.gca().set_xticks([])
        plt.gca().set_yticks([])
        plt.axis('off')
    return
        
def crop_stitched_img(img):
    if len(img.shape)==2:
        h,w = img.shape
        return img[100:h-100,100:w-100]
    elif len(img.shape)==3:
        h, w, _ = img.shape
        return img[100:h-100,100:w-100,:]









def make(filelist, stores, framenums, skipframes=4, nframes=800, flipped=None):

    if flipped == None:
        flipped = ['upper' for x in range(len(filelist))]
    elif np.array(flipped).dtype == int:
        l = np.array(['upper' for x in range(len(filelist))])
        l[np.array(flipped) != 0] = 'lower'
        flipped = list(l)
    elif np.array(flipped).dtype == bool:
        l = np.array(['upper' for x in range(len(filelist))])
        l[bools] = 'lower'
        flipped = list(l)
        

    N = len(filelist)
    if N <=3:
        gridsize=(1,N)
    elif N <=10:
        gridsize=(2,N/2 + N%2)
    elif N <=18:
        gridsize=(3,N/3 + N%3)
    #gridsize = (int(N**0.5), N/int(N**0.5) + N%(int(N**0.5)))
   
    for frame in range(nframes):
        fig = plt.figure(figsize=(gridsize[1]*2, gridsize[0]*2))
        gs1 = gridspec.GridSpec(gridsize[0], gridsize[1])
        gs1.update(wspace=0.025, hspace=0.025)
        for i in range(N):
            ax = fig.add_subplot(gs1[i])
            try:
                img, (f, t) = stores[i].get_image(framenums[i])
                framenums[i] += skipframes
            except:
                img, (f, t) = stores[i].get_next_image()
                framenums[i] = f+skipframes
            
            if '.stitched' in filelist[i]:    
                img = crop_stitched_img(img)
                img = exposure.adjust_sigmoid(img, 0.40, 8)
            ax.imshow(img, cmap='gray', origin=flipped[i])
            plotnice('img')
            ax.set_aspect('equal')
        
        if frame < 100:
            TEXT = 'Stim: OFF '
            props = dict(boxstyle='round', facecolor='#5997d1', alpha=0.5)
        else:
            TEXT = 'Stim: ON'
            props = dict(boxstyle='round', facecolor='#f99a3b', alpha=0.5)
        ax = fig.add_subplot(gs1[-1])
        plotnice('img')
        ax.text(0.95, 0.05, TEXT, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right', bbox=props)
        plt.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
        #plt.show() #FIXME
        plt.savefig('/home/dan/Desktop/up40vid/%04d.png'%frame, dpi=200)
        plt.close('all')
    return


def setup(filelist, prestim_frames=400, **kwargs):
    stores = []
    framenums = []
    for vid in filelist:
        pf = pd.read_pickle(vid + '/track/perframe_stats.pickle')
        log = stims.get_logfile(vid)
        store = imgstore.new_for_filename(vid +'/metadata.yaml')
        stores.append(store)
        ret, pf2 = stims.synch_coherence_with_rotation(pf, log, store)#sync_reversals
        
        pf3 = sync_by_stimStart(pf2)
        startframe = pf3.loc[pf3['stimStart'].idxmax() -prestim_frames, 'FrameNumber'] 
    
        framenums.append(startframe)
    return  filelist, stores, framenums


_flipped = [1,1,1,1,1,0,0,1,0,0]

filelist, stores, framenums = setup(up128)

make(filelist, stores, framenums, nframes=3000)



