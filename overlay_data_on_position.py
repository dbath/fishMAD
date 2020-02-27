

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd
import numpy as np
from scipy import stats
import scipy
import networkx as nx



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


def go(framenum, ts_data):
    img, (_,_) = store.get_image(framenum)
    data = g.get_group(framenum)
    
    fig, a1, a2 = plot_video_with_data_below(img, data, ts_data,
                            timepoint=framenum )
    return fig, data, framenum                        

def get_hull_area(g, q=0.95):
    """
    pass a df grouped by FrameNumber
    """
    h = []
    f = []
    for frame, data in g:
        data['dCentroid'] = distance_from_point(data[XPOS],data[YPOS])   
        dQ = data.loc[data['dCentroid'] < data.quantile(q)['dCentroid'], :]
        h.append(scipy.spatial.ConvexHull(list(zip(dQ[XPOS],dQ[YPOS]))).area)
        f.append(frame)
    return pd.DataFrame({'FrameNumber':f,'hullArea':h})

def distance_from_point(xx, yy, cx=None, cy=None):
    #returns distance from given points (xx and yy) and a defined point, defaults to centre (cx, cy)
    if cx==None:
        cx = xx.median()
    if cy == None:
        cy = yy.median()
    return np.sqrt((xx-cx)**2 + (yy-cy)**2)
    

def plot_video_with_data_below(img, frameData, ts_data, stim=None, timepoint=None, image_width=3666, image_height=3848):

    fig = plt.figure(figsize=(image_width/500, image_height*1.2/500), dpi=200 )
    ax1 = plt.subplot2grid((12,10), (0,0), colspan=10, rowspan=10)
    fig.add_axes(ax1)
    
    
    #plot positions with kernel density
    xx = frameData[XPOS]
    yy = frameData[YPOS]
    kde = stats.gaussian_kde([xx,yy])
    zz = kde([xx,yy])
    
    DENSITY = str(np.around(np.median(zz)*1000000,2))
    
    if stim ==None:
        stim = 'Stim: ' + str(np.around(frameData.coh.mean()*frameData.dir.mean(),1))
    
    plot_data_on_video(img, xx, yy, zz, stim, fig=fig, ax=ax1,
                        xlim=(7,312), ylim=(8,327),_alpha=1.0,
                        colourNorm=(0,0.00008))
    #get 95% of positions closest to group centroid
    frameData['dCentroid'] = distance_from_point(xx,yy)

    d95 = frameData.loc[frameData['dCentroid'] < frameData.quantile(0.95)['dCentroid'], :]
    points = np.array(list(zip(d95[XPOS],d95[YPOS])))
    hull = scipy.spatial.ConvexHull(points) 
    for simplex in hull.simplices:
        ax1.plot(points[simplex, 0], points[simplex, 1], '#FFFFFF')
    AREA = str(np.around(hull.area))
    
    
    props = dict(boxstyle='round', facecolor='#ffffff', alpha=0.5)
    ax1.text(0.02, 0.02, 'Area: ' +AREA, transform=ax1.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='left', bbox=props)
    ax1.text(0.5, 0.02, 'Density: '+DENSITY, transform=ax1.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='center', bbox=props)                    
    ax2 = plt.subplot2grid((12,10), (10,0), colspan=10, rowspan=2)
    fig.add_axes(ax2)
    
    x = ts_data[ts_data.columns[0]]
    for col in ts_data.columns[1:]:
        ax2.plot(x, ts_data[col], label=col)
    
    plt.legend()  
    if not timepoint==None:
        ax2.axvline(x=timepoint, c='#CC3030')
      
    
    plt.subplots_adjust(left=0.0, bottom=0.0, right=1.0, top=1.0, wspace=0.0, hspace=0.0)

    return fig, ax1, ax2

def plot_data_on_video(img, xdata, ydata, colourdata, TEXT, fig=None, ax=None,
                        xlim=(7,312), ylim=(8,327),_alpha=1.0,
                        colourNorm='undefined'):
    if fig==None:
        fig = plt.figure(frameon=False)
        fig.set_size_inches(4,4)
    if ax== None:
        ax = fig.add_subplot(111)
    plt.imshow(crop_stitched_img(img), extent=[xlim[0], xlim[1],ylim[0],ylim[1]], origin='lower')
    
    
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


def plot_network_communities(img, graph, partition, coords, BY='nodes', colours='undefined', fig=None, ax=None, 
                              xlim=(7,312), ylim=(8,327), _alpha=1.0):
    """
    img = an image
    graph = a networkx graph object
    partition: if BY == 'nodes' > pass a dict with nodes as keys and groups as values
               if BY == 'edges' > pass a dict with edges as keys and groups as values
    coords = xy positions to plot, in the form of a dict where {trackid:(x,y)} with trackid as string
    colours = a list
    
    """


    if fig==None:
        fig = plt.figure(frameon=False)
        fig.set_size_inches(4,4)
    if ax== None:
        ax = fig.add_subplot(111)
    if colours=='undefined':
        colours = create_colourlist(len(set(partition.values()))+1, 'hsv')
        
    plt.imshow(crop_stitched_img(img), extent=[xlim[0], xlim[1],ylim[0],ylim[1]], origin='lower')    
    
    count = 0
    if BY=='nodes':
        for com in set(partition.values()) : 
            com_members = [A for A in partition.keys() if partition[A] == com] 
            nx.draw_networkx_nodes(graph, coords, com_members, node_size=3, node_color=colours[count]) 
            count +=1 
        nx.draw_networkx_edges(graph, coords, alpha=0.1, linewidth=0.1) 

    elif BY=='edges':
        for com in set(partition.values()) : 
            com_members = [A for A in partition.keys() if partition[A] == com] 
            if len(com_members) <5:
                continue
            nx.draw_networkx_edges(graph, coords, com_members, edge_color=colours[count], alpha=0.75, linewidth=0.1) 
            count +=1 
        nx.draw_networkx_nodes(graph, coords, node_size=3, color='white') 


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
