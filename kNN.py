import numpy as np
import argparse
from utilities import *
import imgstore
import matplotlib.pyplot as plt
from matplotlib import collections  as mc



    
def distance(A, B):
    return np.sqrt((A[0]-B[0])**2 + (A[1]-B[1])**2)
    
    
def nearestNeighbour(index_of_point, df):
    
    point = tuple(df.loc[index_of_point, [XPOS,YPOS]])
    pointdf = df[df.index != index_of_point]
    pointdf.reset_index(drop=True, inplace=True)
    pointsets = zip(pointdf[XPOS], pointdf[YPOS])
    try:
        pointdf['distance'] = [ distance(point, k) for k in pointsets]
    except:
        print index_of_point, point 
        return np.nan, (np.nan, np.nan), np.nan
    ID = pointdf.loc[pointdf.distance.argmin(), 'trackid']
    loc = tuple(pointdf.loc[pointdf.distance.argmin(), [XPOS,YPOS]])
    dist = distance(point, loc)   
    return ID, loc, dist
    
def getNN(df):
    df.reset_index(drop=True, inplace=True)
    nIDs = []
    nX = []
    nY = []
    nDist = []
    for i in df.index:
        if len(df) > 1:
            a, (b,c),d = nearestNeighbour(i, df)
        else:
            a, (b,c),d = np.nan, (np.nan, np.nan), np.nan
        nIDs.append(a)
        nX.append(b)
        nY.append(c)
        nDist.append(d)
    df['neighbourID'] = nIDs
    df['neighbourX'] = nX
    df['neighbourY'] = nY
    df['neighbourDist'] = nDist
    return df

def plot_NN(ax, data):
    lines = []
    for i in data.index:
        l =  16.0*(data.loc[i, [XPOS, YPOS, 'neighbourX','neighbourY']].values) #FIXME hardcoded scaling
        lines.append([(l[0],l[1]),(l[2],l[3])])
    lc = mc.LineCollection(lines, color='white', linewidth=0.125)
    ax.add_collection(lc)
    return

def plot_hist(fig, ax, dataArray, nbins, xLabel, xLim):
    """
    ax = matplotlib axis object
    dataArray = numpy array with data to be plotted
    nbins = number of bins
    xLabel = label for x axis
    xLim = tuple with min and max values (-100,100)
    
    """
    xLimDif = xLim[1] - xLim[0]
    
    xTicks = list(np.arange(xLim[0]-10, xLim[1], 10) + 10)
    fig.add_axes(ax)
    plt.hist(dataArray, bins=nbins, normed=True, linewidth=0)
    ax.set_xlabel(xLabel, fontsize=2, labelpad=0.2)
    ax.set_xlim(xTicks[0], xTicks[-1])
    ax.set_xticks(xTicks)
    ax.tick_params(axis='x', which='major', labelsize=2, length=1, width=0.1)
    ax.tick_params(axis='y', which='major', labelsize=2, length=0, width=0.0)
    """
    ax.set_ylim(0,0.05)  
    ax.set_yticks([])
    for axis in ['top','right', 'left']:   
        ax.spines[axis].set_visible(False)
    for axis in ['top','bottom','left']:
        ax.spines[axis].set_linewidth(0.1)
    for axis in ['right', 'left']:   
        ax.spines[axis].set_visible(False)
    """
    #ax2.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom') 
    return 


def plot_annotated_image_with_hist(data, img, maxValue):
    width = 0.001*img.shape[0]
    height = 0.001125*img.shape[1]
    fig = plt.figure(figsize=(width,height), dpi=100)
    ax1 = plt.subplot2grid((9,8), (0,0), colspan=8, rowspan=8)
    fig.add_axes(ax1)
    plt.imshow(img, cmap='gray')
    plot_NN(ax1, data)   #plot nearest neighbour lines
    
    a=plt.gca()
    ax1.set_frame_on(False)
    ax1.set_xticks([]); ax1.set_yticks([])
    plt.axis('off')
    plt.xlim(0,img.shape[0])
    plt.ylim(0,img.shape[1])
      
    ax2 = plt.subplot2grid((9,8), (8,0), colspan=8, rowspan=1)
    if data['neighbourDist'].max() > maxValue:
        maxValue = np.round(1.1*data['neighbourDist'].max())
    if len(data) > 1:
        plot_hist(fig, ax2, np.array(data['neighbourDist']), 50, 'Nearest Neighbour Distance (cm)', (0,maxValue))
    else:
        plot_hist(fig, ax2, np.array(pd.Series([0])), 50, 'Nearest Neighbour Distance (cm)', (0,maxValue))
        
    fig.tight_layout()  
    fig.subplots_adjust(wspace=0.00, top=1.0, bottom=0)
    fig.subplots_adjust(hspace=0.00)
    plt.savefig(TRACK_DIR + 'annotated_vid/NN_%06d.png'%(i) , bbox_inches='tight', pad_inches=0, dpi=1000)
    plt.close('all')    
    
    return fig, maxValue
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--v', type=str, required=True,
                        help="path to video's main directory, eg: '/recnode/exp_20170527_162000")
    parser.add_argument('--report', type=str, required=False, default='nn',
                        help='list properties to report, eg: "nn, centroid-position"')
    parser.add_argument('--makevid', type=bool, required=False, default=False,
                        help='make true to make a video')
    parser.add_argument('--fromScratch', type=bool, required=False, default=False,
                        help='make true to discard old info and start from scratch')
    args = parser.parse_args()
    
    MAIN_DIR = slashdir(args.v)  
    TRACK_DIR = MAIN_DIR + 'track/'
    
    
    
    if args.makevid:
        store = imgstore.new_for_filename(MAIN_DIR + '/metadata.yaml' )
        maxValue=30
        if not os.path.exists(TRACK_DIR + 'annotated_vid'):
            os.makedirs(TRACK_DIR + 'annotated_vid')
    if args.fromScratch or not os.path.exists(TRACK_DIR + 'frameByFrame_complete' ):
        if args.fromScratch:
            fbf = getFrameByFrameData(TRACK_DIR, False)
        else:
            fbf = getFrameByFrameData(TRACK_DIR)   
    else:
        fbf = pd.read_pickle(TRACK_DIR + 'frameByFrameData.pickle' )
    
    
    f = fbf.groupby(['frame'])
    frame_stats = pd.DataFrame()
    nn_collection = {}
    nn_angle = {}
    #Perform analysis on each frame:
    for i, data in f:
        data.replace(to_replace=np.inf, value=np.nan, inplace=True)
        data = data.dropna()
        if ('nn' in args.report) or ('neigh' in args.report):
        
            data = getNN(data)
        if args.makevid:
            if not os.path.exists(TRACK_DIR + 'annotated_vid/NN_%06d.png'%(i)):
                img, (vidFrameNum, vidTimestamp) = store.get_image(store.frame_min + i)
            #data = data.dropna().reset_index(drop=True, inplace=True)
                fig, maxValue = plot_annotated_image_with_hist(data, img, maxValue)   
        
        data['nnAngle'] = [angle_from_heading(data.loc[k, [XVEL,YVEL]],data.loc[k, [XPOS,YPOS]],data.loc[k, ['neighbourX','neighbourY']]) for k in data.index]
        
        nn_collection.update({i: np.array(data['neighbourDist'].values)})
        nn_angle.update({i: np.array(data['nnAngle'].values)})
        
        frame_stats.loc[i, 'nnDist_median'] = data['neighbourDist'].median()
        frame_stats.loc[i, 'nnDist_mean'] = data['neighbourDist'].mean()
        frame_stats.loc[i, 'nnDist_std'] = data['neighbourDist'].std()
        frame_stats.loc[i, 'nnAng_median'] = data['nnAngle'].median()
        frame_stats.loc[i, 'nnAng_mean'] = data['nnAngle'].mean()
        frame_stats.loc[i, 'nnAng_std'] = data['nnAngle'].std()
        frame_stats.loc[i, 'nTracks'] = len(data)
        
        if i%500 == 0:
            print "processed frame number :", i
        
    frame_stats.to_pickle(TRACK_DIR + 'frame_stats.pickle') 
    nnDF = pd.DataFrame.from_dict(nn_collection,  orient='index')
    nnDF.to_pickle(TRACK_DIR + 'nearest_neighbour_per_frame.csv')
    
    nnD = getFramelessValues(nn_collection)
    print nnD.shape
    #nnD = nnD[(nnD!= np.nan) and (nnD !=0)]
    np.save(TRACK_DIR + 'nnDistance.npy', nnD)
    np.savetxt(TRACK_DIR + 'nnDistance.txt', nnD, delimiter=',')
    nnA = getFramelessValues(nn_angle)
    #nnA = nnA[(nnA!= np.nan) and (nnA !=0)]
    np.save(TRACK_DIR + 'nnAngle.npy', nnA)
    np.savetxt(TRACK_DIR + 'nnAngle.txt', nnA, delimiter=',')
    
      
    fig = plt.figure()
    ax1 = plt.subplot2grid((2,1), (0,0))
    #fig.add_axes(ax1)
    frame_stats[frame_stats['nnDist_median'] == 0] = np.nan
    plot_hist(fig, ax1, np.array(frame_stats['nnDist_median'].dropna()), 100, 'Median Nearest Neighbour Distance per frame (cm)', (0,150), [0,50,100,150])
    
    ax2 = plt.subplot2grid((2,1), (1,0))
    #fig.add_axes(ax2)
    plot_hist(fig, ax2, np.array(frame_stats['nnDist_std'].dropna()), 100, 'Std of Nearest Neighbour Distance per frame (cm)', (0,50), [0,25,50])
    plt.title(MAIN_DIR.split('/')[-2])
    fig.tight_layout()  
    plt.savefig(TRACK_DIR + 'statistics.svg' , bbox_inches='tight', pad_inches=0)
    
    
