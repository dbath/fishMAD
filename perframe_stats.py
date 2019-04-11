import argparse
import pandas as pd
import numpy as np
from utilities import *
import matplotlib.pyplot as plt
import stim_handling
from pykalman import KalmanFilter
import centroid_rotation
from multiprocessing import Process
import scipy
from scipy.signal import find_peaks

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

        
        
def calculate_perframe_stats(fbf, TRACK_DIR):
    if not SPEED in fbf.columns:
        os.remove(TRACK_DIR + '/frameByFrameData.pickle')
        os.remove(TRACK_DIR + '/frameByFrame_complete')
        fbf = getFrameByFrameData(TRACK_DIR, RESUME=False)
    fbf = fbf.loc[fbf[XPOS].notnull(), :]
    fbf = fbf.loc[fbf[YPOS].notnull(), :]
    fbf.loc[:,'uVX'] = fbf.loc[:,XVEL] / fbf.loc[:,SPEED]
    fbf.loc[:,'uVY'] = fbf.loc[:,YVEL] / fbf.loc[:,SPEED]
    fbf = fbf.drop(columns=['header'])
    f = fbf.groupby(['frame'])
    frame_means = pd.DataFrame(columns=['cx','cy','radius',
                                 'polarization','dRotation','swimSpeed',
                                 'borderDistance'])
    frame_medians = pd.DataFrame(columns=['cx','cy','radius',
                                 'polarization','dRotation','swimSpeed',
                                 'borderDistance'])
    frame_stds = pd.DataFrame(columns=['cx','cy','radius',
                                 'polarization','dRotation','swimSpeed',
                                 'borderDistance'])
    rotation_pdf_centroids = pd.DataFrame(columns=['frame','centroid','height'])
    
    gaussian_X = np.linspace(-1,1,201)
    ARENA_WIDTH = get_arena_width(TRACK_DIR.split('/track')[0])
    for i, data in f:
        #polarization is the length of the average of all unit vectors
        #polarization = abs(np.sqrt((data.loc[:,'uVX'].mean())**2 + (data.loc[:,'uVY'].mean())**2))
        
        
        #angular momentum of fish
        points = np.array(zip(data.loc[:,XPOS], data.loc[:,YPOS]))
        
        if len(points) < 0:
            print "low tracking quality: ", TRACK_DIR.rsplit('/', 3)[1], str(i), str(len(points))
        centroid = get_centroid(points)   
        
        data.loc[:,'CX'] = data.loc[:,XPOS] - centroid[0] # component vector to centroid, X
        data.loc[:,'CY'] = data.loc[:,YPOS] - centroid[1] # component vector to centroid, Y
        data.loc[:,'radius'] = np.sqrt(data.loc[:,'CX']**2 + data.loc[:,'CY']**2)  #radius to centroid
        data.loc[:,'uCX'] = data.loc[:,'CX'] / data.loc[:,'radius'] # X component of unit vector R
        data.loc[:,'uCY'] = data.loc[:,'CY'] / data.loc[:,'radius'] # Y component of unit vector R
        data = data.dropna()
        
        rotation_directed = np.cross(data[['uCX','uCY']], data[['uVX','uVY']])
        
        #Find centroid of PDF of rotation scores fit to gaussian
        peaks, peakParams = scipy.signal.find_peaks(scipy.stats.gaussian_kde(rotation_directed).pdf(gaussian_X),0)
        for j in range(len(peaks)):
            rotation_pdf_centroids = rotation_pdf_centroids.append({'frame':i, 'centroid':gaussian_X[peaks[j]], 'height':peakParams['peak_heights'][j]}, ignore_index=True)
        
        
        #compile mean stats:
        
        m = data.mean()
        row = pd.Series({'cx':centroid[0],
                         'cy':centroid[1],
                         'radius':m['radius'],
                         'polarization':np.sqrt(m['uVX']**2 + m['uVY']**2),
                         'dRotation':rotation_directed.mean(),
                         'swimSpeed':m[SPEED],
                         'borderDistance':m['BORDER_DISTANCE#wcentroid']
                         }, name=i)
                         
        frame_means.append(row)
        
         #compile median stats:
        
        med = data.median()
        row = pd.Series({'cx':centroid[0],
                         'cy':centroid[1],
                         'radius':med['radius'],
                         'polarization':np.sqrt(med['uVX']**2 + med['uVY']**2),
                         'dRotation':rotation_directed.median(),
                         'swimSpeed':med[SPEED],
                         'borderDistance':med['BORDER_DISTANCE#wcentroid']
                         }, name=i)
                         
        frame_medians.append(row)       
        #compile std stats:
        
        std = data.std()
        row = pd.Series({'cx':centroid[0],
                         'cy':centroid[1],
                         'radius':std['radius'],
                         'polarization':np.sqrt(std['uVX']**2 + std['uVY']**2),
                         'dRotation':rotation_directed.std(),
                         'swimSpeed':std[SPEED],
                         'borderDistance':std['BORDER_DISTANCE#wcentroid']
                         }, name=i)
                         
        frame_stds.append(row)      

    centroidRotation = get_centroid_rotation(frame_means, TRACK_DIR, 8, ARENA_WIDTH)
    
    frame_means['centroidRotation'] = centroidRotation
    frame_medians['centroidRotation'] = centroidRotation
        
    frame_means.to_pickle(TRACK_DIR + '/frame_means_rotation_polarization.pickle')
    frame_medians.to_pickle(TRACK_DIR + '/frame_medians_rotation_polarization.pickle')
    frame_stds.to_pickle(TRACK_DIR + '/frame_stds_rotation_polarization.pickle')
    g = rotation_pdf_centroids.groupby('frame')
    rotation_pdf_centroids.index = rotation_pdf_centroids['frame']
    rotation_pdf_centroids['framemaxheight'] = g['height'].max()
    rotation_pdf_centroids['relheight'] = rotation_pdf_centroids['height'] / rotation_pdf_centroids['framemaxheight']
    rotation_pdf_centroids.to_pickle(TRACK_DIR + '/rotation_pdf_centroids.pickle')

    return frame_means, frame_medians, frame_stds 


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
    conv = open(slashdir(_MAIN_DIR) + 'track/conversion.settings')
    SETTINGS = conv.readlines()
    for item in SETTINGS:
        if item.find('real_width') !=-1:
             ARENA_WIDTH = int(item.split(' = ')[1].split('\n')[0]  )
    conv.close()
    return ARENA_WIDTH
    
def get_centroid_rotation(df, trackdir, N_ITER, ARENA_WIDTH=None):
    #GET UNIT VECTORS OF GROUP CENTROID VELOCITY
    """
    """
    MAIN_DIR = '/'.join(trackdir.split('/')[:-1])
    df = df.loc[df.cx.notnull(), :]
    df = df.loc[df.cy.notnull(), :]
    df['cxK'], df['cyK'] = kalman(df[['cx','cy']], N_ITER) #smooth positions before calculating velocity.
    df['vcx'] = df['cxK'] - df.shift()['cxK'] #calculate velocity
    df['vcy'] = df['cyK'] - df.shift()['cyK'] #calculate velocity
    df = df.loc[df.vcx.notnull(), :]
    df = df.loc[df.vcy.notnull(), :]
    
    df['centroidSpeed'] = np.sqrt(df['vcx']**2 + df['vcy']**2)
    df['uVCX'] = df['vcx'] / df['centroidSpeed'] # X component of unit vector
    df['uVCY'] = df['vcy'] / df['centroidSpeed'] # Y component of unit vector
    
    #GET WIDTH OF ARENA TO DEFINE CENTRE
    if ARENA_WIDTH==None:
        ARENA_WIDTH = get_arena_width(MAIN_DIR)
    
    #GET UNIT VECTORS OF GROUP CENTROID POSITION
    df['CX'] = df['cx'] - (ARENA_WIDTH/2.0)
    df['CY'] = df['cy'] - (ARENA_WIDTH/2.0)
    df['radius'] = np.sqrt(df['CX']**2 + df['CY']**2)  #radius to centre of arena
    df['uCX'] = df['CX'] / df['radius'] # X component of unit vector R
    df['uCY'] = df['CY'] / df['radius'] # Y component of unit vector R

    #GET ROTATION ORDER:
    df['centroid_rotation_directed'] = np.cross(df[['uCX','uCY']], df[['uVCX','uVCY']])
    df['centroid_rotation'] = abs(df['centroid_rotation_directed'])
    
    
    return df['centroid_rotation_directed']           

def plot_perframe_vs_time(DIR, subs, ylabs, df=pd.DataFrame(), fn=''):
    if len(df) < 1:
        df = pd.read_pickle(DIR + 'track/frame_means_rotation_polarization.pickle')

    df = df[df['FrameNumber'].notnull()]
    fig  = plt.figure()
    fig.suptitle(DIR.split('/')[-2])
    colourlist = ['black','red','blue', 'orange','purple','green','yellow']
    axes = []
    for x in len(subs):
        ax = fig.add_subplot(len(subs), 1, 1+x)
        axes.append(ax)
    for REP in range(len(subs)):
        ax = axes[REP]
        fig.add_axes(ax)
        plt.plot(df.Time, df[subs[REP]].values, color=colourlist[REP])
        ax.set_title(subs[REP])
        ax.set_ylabel(ylabs[REP])
        if REP == len(subs)-1:
            plt.setp(ax.get_xticklabels(), visible=False)
        else:
            ax.set_xlabel('Time (s)')
        if subs[REP] in ['dRotation','centroidRotation']:
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
    print "processing: ", MAIN_DIR
    #getColumnNames('_'.join(MAIN_DIR.split('/')[-1]..split('.')[0].split('_')[-2:]))
    trackdir = slashdir(MAIN_DIR) + 'track/'

    if os.path.exists(vDir + 'track/frameByFrame_complete'):
        try:
            fbf = pd.read_pickle(trackdir + 'frameByFrameData.pickle')
        except:
            print "CORRUPTED FILE. DELETING frameByFrameData:", trackdir
            os.remove(trackdir + 'frameByFrameData.pickle')
            return
    else:
        fbf = getFrameByFrameData(trackdir, RESUME)
    means, medians, stds = calculate_perframe_stats(fbf, trackdir)
    
    store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml')
    log = get_logfile(MAIN_DIR)
    if 'reversals' in MAIN_DIR:
        ret, means = stim_handling.sync_reversals(means, log, store)
        ret, medians = stim_handling.sync_reversals(medians, log, store)
        ret, stds = stim_handling.sync_reversals(stds, log, store)
        plot_perframe_vs_time(MAIN_DIR, 
            ['dir','polarization','dRotation','centroidRotation',SPEED,'BORDER_DISTANCE#wcentroid'], 
            ['Direction','Pol. Order','Rot. Order','Rot. Order (centroid)','Median Speed','Median Border Distance']
            medians,
            '_median') 
    elif 'coherence' in MAIN_DIR:
        ret, means = stim_handling.synch_coherence_with_rotation(MAIN_DIR, means)
        ret, medians = stim_handling.synch_coherence_with_rotation(MAIN_DIR, medians)
        ret, stds = stim_handling.synch_coherence_with_rotation(MAIN_DIR, stds)
        plot_perframe_vs_time(MAIN_DIR, 
            ['coherence','polarization','dRotation','centroidRotation',SPEED,'BORDER_DISTANCE#wcentroid'], 
            ['Coherence','Pol. Order','Rot. Order','Rot. Order (centroid)','Median Speed','Median Border Distance']
            medians,
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
                    fileList.append(x)
                elif not ('3m_' in x or '3M_' in x):
                    fileList.append(x)
    threadcount = 0
    for filenum in np.arange(len(fileList)):
        vDir = fileList[filenum]
        if os.path.exists(vDir + '/track/converted.results'):
            if not os.path.exists(vDir + '/track/vsTime_perframe_stats.png'):
                if os.path.exists(vDir + '/track/frameByFrameData.pickle'):
                    if getModTime(vDir + '/track/frameByFrameData.pickle') < getTimeFromTimeString('20190315_130000'):
                        os.remove(vDir + '/track/frameByFrameData.pickle')
                        os.remove(vDir + '/track/frameByFrame_complete')
                
                #try:
                p = Process(target=run, args=(vDir,args.resume))
                p.start()
                threadcount += 1
                
                if p.is_alive():
                    if (threadcount >= args.maxthreads) or (filenum == len(fileList)):
                        threadcount = 0
                        p.join()

