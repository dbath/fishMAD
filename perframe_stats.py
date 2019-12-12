import argparse
import pandas as pd
pd.options.mode.chained_assignment = 'raise'
import pickle
import numpy as np
np.warnings.filterwarnings('ignore')
import time
from concurrent.futures import ProcessPoolExecutor, as_completed #for multiprocessing
from utilities import *
import matplotlib.pyplot as plt
import stim_handling
#from pykalman import KalmanFilter
#import centroid_rotation
from multiprocessing import Process
import scipy
from scipy.signal import find_peaks
import imgstore
import shutil
import traceback
import joblib


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
    try:
        length = arr.shape[0]
        sum_x = np.sum(arr[:, 0])
        sum_y = np.sum(arr[:, 1])
        return sum_x/length, sum_y/length
    except:
        return (np.nan, np.nan)


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


def process_chunk(df):

    df = df.copy()
    f = df.groupby('frame')
    maxFrame = df.frame.max()
    if maxFrame%args.maxthreads == 0:
        progressbar = True
    else:
        progressbar = False
    perframe_stats = pd.DataFrame()
    #rotation_pdf_centroids = pd.DataFrame(columns=['frame','centroid','height'])
    
    gaussian_X = np.linspace(-1,1,201)  #FIXME move to global?

    rotations_cMass = {}
    rotations_cArea = {}
    for i, data in f:
        try:
            #angular momentum of fish
            points = np.array(zip(data.loc[:,XPOS], data.loc[:,YPOS]))
            
            if len(points) < 0:
                print("low tracking quality: ", TRACK_DIR.rsplit('/', 3)[1], str(i), str(len(points)))
            centroid = get_centroid(points)   

            CX = data.loc[:,XPOS]- centroid[0]
            CY = data.loc[:,YPOS] - centroid[1]
            radius = np.sqrt(CX**2 + CY**2)
            
            rotationOrder_cMass = rotationOrder(centroid[0], centroid[1], 
                                                data.loc[:,XPOS], data.loc[:,YPOS], 
                                                data.loc[:,'uVX'], data.loc[:,'uVY'])
            
            rotationOrder_cArea = rotationOrder(ARENA_WIDTH/2.0, ARENA_WIDTH/2.0, 
                                                data.loc[:,XPOS], data.loc[:,YPOS], 
                                                data.loc[:,'uVX'], data.loc[:,'uVY'])
            
            
            #Find centroid of PDF of rotation scores fit to gaussian
            try:
                peaks, peakParams = scipy.signal.find_peaks(scipy.stats.gaussian_kde(rotationOrder_cArea).pdf(gaussian_X),0)
            except:
                peaks = []
                peakParams = []
                
            if len(peaks) == 0:
                Peak_1 = np.nan
                PeakHeight_1 = np.nan
                Peak_2 = np.nan
                PeakHeight_2 = np.nan
            elif len(peaks) < 2:
                Peak_1 = gaussian_X[peaks[peakParams['peak_heights'].argmax()]]
                PeakHeight_1 = peakParams['peak_heights'].max()
                Peak_2 = np.nan
                PeakHeight_2 = np.nan
            else:
                first, second = pd.DataFrame(peakParams)['peak_heights'].nlargest(2).index
                Peak_1 = gaussian_X[peaks[first]]
                PeakHeight_1 = peakParams['peak_heights'][first]
                Peak_2 = gaussian_X[peaks[second]]
                PeakHeight_2 = peakParams['peak_heights'][second]
            #because some things cant handle nans :(
            rA = rotationOrder_cArea[np.isfinite(rotationOrder_cArea)]
            rM = rotationOrder_cMass[np.isfinite(rotationOrder_cMass)]
            
            #compile mean stats:
            m = data.mean().copy()
            med = data.median().copy()
            std = data.std().copy()
            row = pd.Series({'cx':centroid[0],
                             'cy':centroid[1],
                             'mean_radius':radius.mean(),
                             'mean_polarization':np.sqrt(m['uVX']**2 + m['uVY']**2),
                             'mean_dRotation_cMass':rM.mean(),
                             'mean_dRotation_cArea':rA.mean(),
                             'mean_swimSpeed':m[SPEED],
                             'mean_borderDistance':m['BORDER_DISTANCE#wcentroid'],
                             'median_radius':radius.median(),
                             'median_polarization':np.sqrt(med['uVX']**2 + med['uVY']**2),
                             'median_dRotation_cMass':np.median(rM),
                             'median_dRotation_cArea':np.median(rA),
                             'median_swimSpeed':med[SPEED],
                             'median_borderDistance':med['BORDER_DISTANCE#wcentroid'],
                             'std_radius':radius.std(),
                             'std_polarization':np.sqrt(std['uVX']**2 + std['uVY']**2),
                             'std_dRotation_cMass':rM.std(),
                             'std_dRotation_cArea':rA.std(),
                             'std_swimSpeed':std[SPEED],
                             'std_borderDistance':std['BORDER_DISTANCE#wcentroid'],
                             'pdfPeak1':Peak_1,
                             'pdfPeak2':Peak_2,
                             'pdfPeak1_height':PeakHeight_1,
                             'pdfPeak2_height':PeakHeight_2,
                             'entropy_Ra':scipy.stats.entropy(np.histogram(rA, bins=100)[0]),
                             'entropy_Ra_nBins':scipy.stats.entropy(np.histogram(rA, bins=len(data))[0])
                             }, name=i)
            perframe_stats = perframe_stats.append(row)
            rotations_cMass[i] = np.array(rM) #excludes nans
            df.loc[data.index, 'rotation_cMass'] = rotationOrder_cMass
            rotations_cArea[i] = np.array(rA) #excludes nans
            df.loc[data.index, 'rotation_cArea'] = rotationOrder_cArea
            if progressbar == True:
                printProgressBar(i,maxFrame, prefix='Frame by frame processing: ') 
        except:
            traceback.print_exc()
    return perframe_stats, rotations_cMass, rotations_cArea, df


def calculate_perframe_stats(fbf, TRACK_DIR, nCores=8):

    # SETUP PARALLEL PROCESSING

    ppe = ProcessPoolExecutor(nCores)
    futures = []
    statResults = []
    rotMResults = []
    rotAResults = []
    fishR = []
    
    # PREPARE DATAFRAME
    fbf = fbf.loc[fbf[XPOS].notnull(), :]
    fbf = fbf.loc[fbf[YPOS].notnull(), :]
    fbf.loc[:,'uVX'] = fbf.loc[:,XVEL] / fbf.loc[:,SPEED]
    fbf.loc[:,'uVY'] = fbf.loc[:,YVEL] / fbf.loc[:,SPEED]
    fbf = fbf.drop(columns=['header'])
    fbf['coreGroup'] = fbf['frame']%nCores  #divide into chunks labelled range(nCores)
    fbf.reset_index(inplace=True)
    # INITIATE PARALLEL PROCESSES
    for n in range(nCores):
        p = ppe.submit(process_chunk, fbf.loc[fbf['coreGroup'] == n, :])
        futures.append(p)
    
    # COLLECT PROCESSED DATA AS IT IS FINISHED    
    for future in as_completed(futures):
        stats, rotM, rotA, fish = future.result()
        statResults.append(stats)
        rotMResults.append(rotM)
        rotAResults.append(rotA)
        fishR.append(fish)
    
    #CONCATENATE RESULTS
    perframe_stats = pd.concat(statResults)
    rotationDf = pd.concat(fishR)
    
    rotationOrders_cMass = {}
    for r in rotMResults:
        rotationOrders_cMass.update(r)
    pick = open(TRACK_DIR + '/rotationOrders_cMass.pickle', "wb")
    pickle.dump(rotationOrders_cMass, pick)
    pick.close()
    
    rotationOrders_cArea = {}
    for r in rotAResults:
        rotationOrders_cArea.update(r)
    pick = open(TRACK_DIR + '/rotationOrders_cArea.pickle', "wb")
    pickle.dump(rotationOrders_cArea, pick)
    pick.close()
    

    ARENA_WIDTH = get_arena_width(TRACK_DIR.split('/track')[0])
    perframe_stats.loc[:,'centroidRotation'] = get_centroid_rotation(perframe_stats, TRACK_DIR,  ARENA_WIDTH)
    log = stim_handling.get_logfile(TRACK_DIR.rsplit('/',1)[0])
    store = imgstore.new_for_filename(TRACK_DIR.rsplit('/',1)[0] + '/metadata.yaml')
    ret, perframe_stats = stim_handling.sync_data(perframe_stats, log, store) 
    perframe_stats.to_pickle(TRACK_DIR + '/perframe_stats.pickle')
    rotationDF.to_pickle(TRACK_DIR + '/frameByFrameData.pickle')

    return perframe_stats


    
    
def get_rotation(data):
    """
    pass a df from a single video frame (a product of groupby('frame'))
    returns the df with rotational vectors and a second series with rotation scores
    """
    points = np.array(zip(data.loc[:,XPOS], data.loc[:,YPOS]))
    centroid = get_centroid(points) 
    data.loc[:,'CX'] = data.loc[:,XPOS] - centroid[0]
    data.loc[:,'CY'] = data.loc[:,YPOS] - centroid[1]
    data.loc[:,'radius'] = np.sqrt(data.loc[:,'CX']**2 + data.loc[:,'CY']**2)
    data.loc[:,'uCX'] = data.loc[:,'CX'] / data.loc[:,'radius']
    data.loc[:,'uCY'] = data.loc[:,'CY'] / data.loc[:,'radius']
    #data = data.dropna()
    rotation_directed = np.cross(data[['uCX','uCY']], data[['uVX','uVY']])
    return data, rotation_directed
    

def plot_gaussian(f, n, fig=None, ax1=None, plotpeaks=False):
    """
        pass a fbf dataframe grouped by frame (f) and a frame number (n).
        plots a histogram of heading directions and a pdf of a gaussian kde of the headings.
    """
    data = f.get_group(n)
    data, rotation_directed = get_rotation(data)
    rotation_directed = rotation_directed[~np.isnan(rotation_directed)]
    X = np.linspace(-1,1,201)
    results, edges = np.histogram(rotation_directed, bins=X, density=True)
    binWidth=edges[1] - edges[0]
    
    if fig== None:
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
    ax1.bar(edges[:-1], results*binWidth, binWidth, color='darkorange')
    ax1.set_ylabel('Frequency', size=14, color='darkorange')
    ax1.tick_params('y', colors='darkorange')
    ax1.set_ylim(0,0.5)
    ax1.set_xlabel('Direction relative to group centroid')
    ax2 = ax1.twinx()
    #plt.hist(rotation_directed, bins=201, normed=True)
    ax2.plot(X, scipy.stats.gaussian_kde(rotation_directed).pdf(X), linewidth=2, color='royalblue')
    if plotpeaks:
        peaks, peakParams = scipy.signal.find_peaks(scipy.stats.gaussian_kde(rotation_directed).pdf(X),0)
        for j in range(len(peaks)):
            a = peakParams['peak_heights'][j] / 1.0
            if a > 1.0:
                a = 1.0
            ax1.plot(X[peaks[j]], 0.45, markeredgecolor='royalblue',
                        markerfacecolor='royalblue', 
                        markersize=10.0, 
                        alpha=a, marker="o")
            ax1.plot(X[np.abs(X - rotation_directed.mean()).argmin()], 0.45, markeredgecolor='black',
                        markerfacecolor='black', 
                        markersize=5.0, marker="o")
            ax1.plot(X[np.abs(X - np.median(rotation_directed)).argmin()], 0.45, markeredgecolor='red',
                        markerfacecolor='red', 
                        markersize=5.0, marker="o")
            ax1.plot(-1.0*data['dir'].mean(), 0.35, markeredgecolor='black',
                        markerfacecolor='black', 
                        markersize=15.0, marker="*")
            #plt.axvline(x=X[peaks[j]], c='royalblue', alpha=a, linewidth=2)
            #plt.axvline(x=X[np.abs(X - rotation_directed.mean()).argmin()], c='black', linewidth=1)
            #plt.axvline(x=X[np.abs(X - np.median(rotation_directed)).argmin()], c='red', linewidth=1)
    ax2.set_ylim(0,2.5)
    ax2.set_ylabel('Probability density',  color='royalblue')
    ax2.set_yticks([])
    plt.xticks([-1,0,1],['ccw','normal','cw'])
    fig.tight_layout()
    return fig, rotation_directed

from skimage import exposure

def plot_image(img, ax):
    h, w, _ = img.shape
    img = img[100:h-100, 100:w-100, :]
    plt.setp(ax.get_yticklabels(), visible=False)
    plt.setp(ax.get_xticklabels(), visible=False)
    ax.imshow(exposure.adjust_sigmoid(img, 0.40, 8))
    ax.set_xticks([]); ax.set_yticks([])
    return    
"""
MAIN_DIR = '/media/recnodes/recnode_2mfish/reversals3m_512_dotbot_20181017_111201.stitched/'
store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml')
fbf = pd.read_pickle(MAIN_DIR + 'track/frameByFrameData.pickle')
ret, fbf = sync_reversals(fbf, get_logfile(MAIN_DIR), store)
fbf = fbf.loc[fbf[XPOS].notnull(), :]
fbf = fbf.loc[fbf[YPOS].notnull(), :]
fbf.loc[:,'uVX'] = fbf.loc[:,XVEL] / fbf.loc[:,SPEED]
fbf.loc[:,'uVY'] = fbf.loc[:,YVEL] / fbf.loc[:,SPEED]
fbf = fbf.drop(columns=['header'])
df = fbf.groupby(['frame'])
"""
def plot_data_above_image(framenumber=None, image_width=3666, image_height=3848, saveas=None, plotpeaks=True):
    """
    requires global variables "store", "df" (grouped by frame number)
    """
    if framenumber==None:
        img, (f,t) = store.get_next_image()
    else:
        img, (f,t) = store.get_image(store.frame_min + framenumber)
    
    fig = plt.figure(figsize=(image_width/500, image_height*1.2/500), dpi=200 )
    ax1 = plt.subplot2grid((12,10), (0,0), colspan=10, rowspan=10)
    fig.add_axes(ax1)
    plot_image(img, ax1)
    ax2 = plt.subplot2grid((12,10), (10,0), colspan=10, rowspan=2)
    fig.add_axes(ax2)
    fig, rotation = plot_gaussian(df, framenumber, fig, ax2, plotpeaks=plotpeaks)
    plt.subplots_adjust(left=0.0, bottom=0.0, right=1.0, top=1.0, wspace=0.0, hspace=0.0)
    if saveas == None:
        return fig, rotation
    else:
        plt.savefig(saveas, bbox_inches='tight', pad_inches=0)
        plt.close('all')
        return rotation
    



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




def get_arena_width(MAIN_DIR):
    conv = open(slashdir(MAIN_DIR) + 'track/conversion.settings')
    SETTINGS = conv.readlines()
    for item in SETTINGS:
        if item.find('real_width') !=-1:
             ARENA_WIDTH = int(item.split(' = ')[1].split('\n')[0]  )
    conv.close()
    return ARENA_WIDTH
    
def get_centroid_rotation(df, trackdir, ARENA_WIDTH=None):
    #GET UNIT VECTORS OF GROUP CENTROID VELOCITY
    """
    """
    MAIN_DIR = '/'.join(trackdir.split('/')[:-1])
    df = df.loc[df.cx.notnull(), :]
    df = df.loc[df.cy.notnull(), :]
    #smooth positions before calculating velocity.
    df.loc[:,'cx_smoothed'] = df['cx'].rolling(5, center=True).mean()
    df.loc[:,'cy_smoothed'] = df['cy'].rolling(5, center=True).mean()
    df.loc[:,'vcx'] = df['cx_smoothed'] - df.shift()['cx_smoothed'] #calculate velocity
    df.loc[:,'vcy'] = df['cy_smoothed'] - df.shift()['cy_smoothed'] #calculate velocity
    df = df.loc[df.vcx.notnull(), :]
    df = df.loc[df.vcy.notnull(), :]
    
    df.loc[:,'centroidSpeed'] = np.sqrt(df['vcx']**2 + df['vcy']**2)
    df.loc[:,'uVCX'] = df['vcx'] / df['centroidSpeed'] # X component of unit vector
    df.loc[:,'uVCY'] = df['vcy'] / df['centroidSpeed'] # Y component of unit vector
    
    #GET WIDTH OF ARENA TO DEFINE CENTRE
    if ARENA_WIDTH==None:
        ARENA_WIDTH = get_arena_width(MAIN_DIR)
    
    #GET UNIT VECTORS OF GROUP CENTROID POSITION
    df.loc[:,'CX'] = df['cx'] - (ARENA_WIDTH/2.0)
    df.loc[:,'CY'] = df['cy'] - (ARENA_WIDTH/2.0)
    df.loc[:,'radius'] = np.sqrt(df['CX']**2 + df['CY']**2)  #radius to centre of arena
    df.loc[:,'uCX'] = df['CX'] / df['radius'] # X component of unit vector R
    df.loc[:,'uCY'] = df['CY'] / df['radius'] # Y component of unit vector R

    #GET ROTATION ORDER:
    df.loc[:,'centroid_rotation_directed'] = np.cross(df[['uCX','uCY']], df[['uVCX','uVCY']])
    #df['centroid_rotation'] = abs(df['centroid_rotation_directed'])
    
    
    return df['centroid_rotation_directed']           

def plot_perframe_vs_time(DIR, subs, ylabs, df=pd.DataFrame(), fn=''):
    if len(df) < 1:
        df = pd.read_pickle(DIR + 'track/perframe_stats.pickle')

    df.dropna(subset=['FrameNumber'], inplace=True)
    if 'dir' in df.columns:
        df.loc[:,'dir'] = -1.0*df.loc[:,'dir']
    fig  = plt.figure(figsize=(4, 2*len(subs)))
    fig.suptitle(DIR.split('/')[-2])
    colourlist = ["#91b43f","#7463cd","#54bc5b","#c560c7","#49925d","#cf4085","#49bfba",
          "#cf4d2b","#6f8bce","#dd862f","#98558b",
          "#c7a745","#dd85a8", "#777d35","#c64855",
          "#9b5e2f","#e0906e"]
    #colourlist = ['black','red','blue', 'orange','purple','green','brown']
    axes = []
    for x in range(len(subs)):
        ax = fig.add_subplot(len(subs), 1, 1+x)
        axes.append(ax)
    for REP in range(len(subs)):
        ax = axes[REP]
        fig.add_axes(ax)
        plt.plot(df.Time, df[subs[REP]].values, color=colourlist[REP])
        #ax.set_title(subs[REP])
        ax.set_ylabel(ylabs[REP])
        if REP == len(subs)-1:
            plt.setp(ax.get_xticklabels(), visible=False)
        else:
            ax.set_xlabel('Time (s)')
        if 'Rotation' in subs[REP]:
            ax.set_ylim(-1.1,1.1)
            ax.set_yticks([-1,0,1])
            plt.axhline(y=0.0, color='k', linestyle='-')
        elif subs[REP] == 'dir':
            ax.set_ylim(-1.3,1.3)
            ax.set_yticks([-1,0,1])
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
            pass
            #ax.set_ylim(0,1) 
            #ax.set_yticks([0,0.5,1])
    #ax.legend(loc=0)
    #plt.colorbar()
    plt.savefig(DIR + 'track/vsTime_perframe_stats'+fn + '.svg', bbox_inches='tight',pad_inches = 0)
    plt.savefig(DIR + 'track/vsTime_perframe_stats'+fn + '.png')#, bbox_inches='tight',pad_inches = 0)
    plt.close('all')
    return


    
def run(MAIN_DIR, RESUME=True):
    print("processing: ", MAIN_DIR)
    #getColumnNames('_'.join(MAIN_DIR.split('/')[-1]..split('.')[0].split('_')[-2:]))
    trackdir = slashdir(MAIN_DIR) + 'track/'
    PF_DONE = False
    if os.path.exists(trackdir + 'perframe_stats.pickle'):  
        perframe_stats = pd.read_pickle(trackdir + 'perframe_stats.pickle')
        if 'dir' in perframe_stats.columns: 
            PF_DONE = True
    if PF_DONE == False:
        if os.path.exists(trackdir + 'frameByFrameData.pickle'):
            try:
                fbf = joblib.load(trackdir + 'frameByFrameData.pickle')
            except:
                print("CORRUPTED FILE. DELETING frameByFrameData:", trackdir)
                os.remove(trackdir + 'frameByFrameData.pickle')
                return
        else:
            fbf = getFrameByFrameData(trackdir, RESUME, args.maxthreads)
        
        if not 'VX#smooth#wcentroid' in fbf.columns:
            print('VX#smooth#wcentroid', "not found in columns.", MAIN_DIR)
            print(fbf.columns)
            os.remove(trackdir + 'frameByFrameData.pickle')
            shutil.rmtree(trackdir + 'fishdata')
            if os.path.exists(trackdir + 'frameByFrame_complete'):
                os.remove(trackdir + 'frameByFrame_complete')    
            return
        
        if len(set(fbf.frame)) < 501:
            print("FOUND INCOMPLETE TRACKING DATA. DELETING TRACKDIR")
            shutil.rmtree(trackdir)
            return
        perframe_stats = calculate_perframe_stats(fbf, trackdir, args.maxthreads)
    
    store = imgstore.new_for_filename(slashdir(MAIN_DIR) + 'metadata.yaml')
    log = stim_handling.get_logfile(MAIN_DIR)
    if 'reversals' in MAIN_DIR:
        #ret, perframe_stats = stim_handling.sync_reversals(perframe_stats, log, store)
        plot_perframe_vs_time(slashdir(MAIN_DIR),         ['dir','median_polarization','median_dRotation_cMass','median_dRotation_cArea','median_swimSpeed','entropy_Ra'], 
            ['Direction','Pol. Order','Rot. Order (CofM)','Rot. Order (Area)','Median Speed', 'Entropy'],
            perframe_stats,
            '_median') 
    elif 'coherence' in MAIN_DIR:
        #ret, perframe_stats = stim_handling.synch_coherence_with_rotation(perframe_stats, log, store)
        plot_perframe_vs_time(slashdir(MAIN_DIR),  ['coherence','median_polarization','median_dRotation_cMass','median_dRotation_cArea','median_swimSpeed', 'entropy_Ra'], 
            ['Coherence','Pol. Order','Rot. Order (CofM)','Rot. Order (Area)','Median Speed','Entropy'],
            perframe_stats,
            '_median') 
    elif 'cogs' in MAIN_DIR:

        pass #FIXME 
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=False, default = '/media/recnodes/recnode_2mfish',help='path to directory')
    parser.add_argument('--handle', type=str, required=False, default='_dotbot_,_jwj_', 
                        help='provide unique identifier (or comma-separated list) to select a subset of directories.')
    parser.add_argument('--maxthreads', type=int, required=False, default=20, 
                        help='maximum number of threads to use in parallel.')
    parser.add_argument('--resume', type=bool, required=False, default=True,
                        help='make false to discard partially-generated pickle files and start from scratch')

                
    args = parser.parse_args()
    
    HANDLE = args.handle.split(',')
    
    
    DIRECTORIES = args.dir.split(',')

        
    fileList = []
    for term in HANDLE:
        for DIR in DIRECTORIES:
            for x in glob.glob(slashdir(DIR) + '*' + term + '*'):
                #select only stitched files from 3m tank, not quadrants.
                if ('3m_' in x or '3M_'  in x) and '.stitched' in x:
                    if '.stitchedx' in x:
                        continue
                    fileList.append(x)
                elif ('3m_' in x or '3M_'  in x) and '.partial_XXXstitch' in x: #FIXME
                    fileList.append(x)
                elif not ('3m_' in x or '3M_' in x):
                    fileList.append(x)
    threadcount = 0
    for filenum in np.arange(len(fileList)):
        vDir = fileList[filenum]
        if os.path.exists(vDir + '/track/converted.results'):
            if not os.path.exists(vDir + '/track/rotationOrders_cXXXArea.pickle'): #FIXME
                try:
                
                    ARENA_WIDTH = get_arena_width(vDir)
                    run(vDir, args.resume)
                except:# Exception as e:
                    print("ERROR: ", vDir)
                    traceback.print_exc()
                    #print e
                """
                #try:
                p = Process(target=run, args=(vDir,args.resume))
                p.start()
                threadcount += 1
                
                if p.is_alive():
                    if (threadcount >= args.maxthreads) or (filenum == len(fileList)):
                        threadcount = 0
                        p.join()
                """
