"""
import numpy as np
import matplotlib.pyplot as plt
from shapely.ops import polygonize,unary_union
from shapely.geometry import LineString, MultiPolygon, MultiPoint, Point
from scipy.spatial import Voronoi

"""
###############################################################################

#find all points that share an edge:
from scipy.spatial import Delaunay
from collections import defaultdict
import itertools
from utilities import *
import stim_handling
import imgstore
import joblib

def distance(A, B):
    return np.sqrt((A[0]-B[0])**2 + (A[1]-B[1])**2)

def get_centroid(arr):
    try:
        length = arr.shape[0]
        sum_x = np.sum(arr[:, 0])
        sum_y = np.sum(arr[:, 1])
        return sum_x/length, sum_y/length
    except:
        return (np.nan, np.nan)

def rotation_and_polarization(centreX, centreY, posX, posY, velX, velY):
    """
    centre - a single point marking the axis of rotation
    pos - position of agents (1 per agent)
    vel - velocity of agents (1 per agent)
    
    Returns: (median rotation, polarization), 1d array of rotation order values
    """
    CX = posX - centreX
    CY = posY - centreY
    radius = np.sqrt(CX**2 + CY**2)
    uCX = CX / radius # X component of unit vector R
    uCY = CY / radius # Y component of unit vector R 
    speed = np.sqrt(velX**2 + velY**2)
    uVX = velX / speed
    uVY = velY  / speed  
    rotationOrder = np.cross(pd.DataFrame({'uCX':uCX,'uCY':uCY}), pd.DataFrame({'velX':uVX, 'velY':uVY}))

    # polarization
    
    p = np.sqrt(uVX.mean()**2 + uVY.mean()**2)
    
    
    return (np.median(rotationOrder), p), rotationOrder



def plot_delaunay(tri, points, trackIDs, xlim=(7,312), ylim=(8,327), fig=None, ax=None, img='not_defined',
                  _alpha=1.0):
    """
    tri: an object of scipy.spatial.Delaunay made from points eg (tri = Delaunay(points))
    points: x and y positions to plot in format: np.array(zip(data[XPOS],data[YPOS]))
    trackIDs: string values to label points, in same order as 'points'
    """
    if fig==None:
        fig = plt.figure(frameon=False)
        fig.set_size_inches(4,4)
    if ax== None:
        ax = fig.add_subplot(111)
    if img == 'not_defined':
        pass
    else:
        plt.imshow(crop_stitched_img(img), extent=[xlim[0], xlim[1],ylim[0],ylim[1]], origin='lower')#Axes(fig, [0., 0., 1., 1.]) 
    plt.triplot(points[:,0], points[:,1], tri.simplices, color='#00FF00FF', linewidth=0.5, alpha=0.5*_alpha)
    plt.plot(points[:,0], points[:,1], 'o', color='#FFFF00FF', markersize=1, alpha=0.3*_alpha)
    for i,p in enumerate(points):
        plt.text(p[0], p[1], trackIDs.iloc[i], ha='center', fontsize=3, fontstyle='italic', fontweight='light', alpha=_alpha)
    plt.gca().set_aspect(1.0)
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
            hspace = 0, wspace = 0)    
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
    return fig




def neighbourhoodWatch(focal, neighbours):
    """
    pass dfs representing the focal indiv and neighbours, returns:
    
    local polarization and rotation of the neighbourhood relative to focal indiv
    'torsion' of neighbourhood - degree to which the neighbourhood is turning toward the centre
    
    how much are the neighbours turning? 
    to what degree does focal's acceleration match the neighbourhood?
            does it match those with which direction is similar?
                or dissimilar?
                
    
    """

    # calculate distance for all neighbours
    neighbours.loc[:,'distance'] = [distance(list(focal[[XPOS,YPOS]].values), list(i[[XPOS,YPOS]].values)) for _,i in neighbours.iterrows()]
    
    # calculate speed relative to neighbours
    neighbours.loc[:,'deltaSpeed'] = focal[SPEED] - neighbours[SPEED]
    
    # calculate difference in radius to arena/group centre, 
    # positive means neighbour is closer to centre
    neighbours.loc[:,'dRad_arena'] = focal['posRadius'] - neighbours['posRadius']
    neighbours.loc[:,'dRad_group'] = focal['grpRadius'] - neighbours['grpRadius']
    
    # calculate rotation & polarization
    (ROTATION, POLARIZATION), neighbours.loc[:,'local_rotation'] = rotation_and_polarization(focal[XPOS], focal[YPOS], neighbours[XPOS], neighbours[YPOS], neighbours[XVEL], neighbours[YVEL])
    
    neighbours['uVX'] = neighbours['VX#smooth#wcentroid']/neighbours[SPEED]
    neighbours['uVY'] = neighbours['VY#smooth#wcentroid']/neighbours[SPEED]
    focal['uVX'] = focal['VX#smooth#wcentroid']/focal[SPEED]
    focal['uVY'] = focal['VY#smooth#wcentroid']/focal[SPEED]
    
    # calculate dTheta, the difference in heading of all neighbours relative to focal
    neighbours.loc[:,'dTheta'] =  np.cross(focal[['uVX','uVY']],neighbours[['uVX','uVY']])
    dTHETA = np.mean(neighbours['dTheta'])
    # compare dTheta on the inside vs outside (relative to arena centre)
    #TORSION = np.mean(neighbours['dTheta'] / neighbours['dRad_arena']) #FIXME does this even make sense?
    
    ACCEL_A = np.mean(neighbours['ANGULAR_A#wcentroid'])
    dACCEL_A = np.mean(focal['ANGULAR_A#wcentroid'] - neighbours['ANGULAR_A#wcentroid'])
    
    
    
    
    
    return



    

def delaunayNeighbours(data, CENTRE=(160,160)):
    """ 
    get neighbours based on Delaunay triangulation (similar to Voronoi tesselation,
    but the math is more straightforward...)
    """
    #data = pd.read_pickle('/home/dan/Desktop/temp_data.pickle')
    points = np.array(zip(data[XPOS],data[YPOS]))
    
    # radius to arena centre
    data['posRadius'] = [distance(list(i[[XPOS,YPOS]].values), CENTRE) for _,i in data.iterrows()]
    
    # radius to group centroid
    GROUP_CENTROID = get_centroid(points)
    data['grpRadius'] = [distance(list(i[[XPOS,YPOS]].values), GROUP_CENTROID) for _,i in data.iterrows()]

    tri = Delaunay(points)
    neiList=defaultdict(set)

    for p in tri.vertices:
        for i,j in itertools.combinations(p,2):
            neiList[i].add(j)
            neiList[j].add(i)


    return tri, neiList, data



def doit(MAIN_DIR, saveas="Not_defined"):
    MAIN_DIR = slashdir(MAIN_DIR) #sometimes people call dirs without a trailing slash
    if saveas == 'Not_defined':
        saveas = MAIN_DIR + 'voronoi_overlay'
    if not os.path.exists(saveas):
        os.makedirs(saveas)
    fbf = joblib.load(MAIN_DIR + 'track/frameByFrameData.pickle')
    fbf = fbf.replace(to_replace=np.inf, value=np.nan)
    

    #filter out tracked reflections by removing tracks that are always near the border
    foo = fbf.groupby('trackid').median()['BORDER_DISTANCE#wcentroid']
    fbf = fbf[~(fbf.trackid.isin(foo[foo<40].index))]

    store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml')
    
    ret, fbf = stim_handling.sync_data(fbf, stim_handling.get_logfile(MAIN_DIR), store)
        
    xlim=(7,312)
    ylim=(8,327)
    f = fbf.groupby(['frame'])
    for i, data in f:
        data = data.replace(to_replace=np.inf, value=np.nan)
        data = data[data[XPOS].notnull()]
        data = data[data[YPOS].notnull()]
        data = data[(data[XPOS].between(xlim[0], xlim[1])) * (data[YPOS].between(ylim[0], ylim[1]))]
        points = np.array(zip(data[XPOS],data[YPOS]))
        TRIANGULATION, NEIGHBOURS, DATA = delaunayNeighbours(data)
        
        if 0: #FIXME put some actual data analysis here.
            for key in sorted(NEIGHBOURS.iterkeys()):
                neighbourhoodWatch(data.iloc[key], data.iloc[list(NEIGHBOURS[key])].reset_index())
            
        
        IMG, (fn, ts) = store.get_image(data.iloc[-1]['FrameNumber'])
        if i < 300:
            FIG = plot_delaunay(TRIANGULATION, points,  DATA['trackid'], img=IMG, _alpha=(float(i/300.0)))
        elif i < 600:
            FIG = plot_delaunay(TRIANGULATION, points,  DATA['trackid'], img=IMG, _alpha=1.0)
        elif i < 900:
            FIG = plot_delaunay(TRIANGULATION, points,  DATA['trackid'], _alpha=1.0)
        else:
            FIG = plot_delaunay(TRIANGULATION, points,  DATA['trackid'], img=IMG, _alpha=1.0)

        plt.savefig(saveas + "/%06d.png"%i, dpi=300)
        plt.close('all')
    
    
    return


if __name__ == "__main__":
    import argparse
    import glob
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=False, default='/media/recnodes/recnode_2mfish/',
			 help='path to directory containing checker vids')
    parser.add_argument('--handle', type=str, required=True, help='unique identifier that marks the files to process. Ideally use the timestamp of the recording, ie "20180808_153229".')
    
    args = parser.parse_args()
    HANDLE = args.handle.split(',')
    DIRECTORIES = args.dir.split(',')
    for x in range(len(DIRECTORIES)):
        if DIRECTORIES[x][-1] != '/':
            DIRECTORIES[x] += '/'
            
    for term in HANDLE:
        for DIR in DIRECTORIES:
            for vDir in glob.glob(DIR + '*' + term + '*.stitched'):
                doit(vDir)
                
                
"""
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
vor = Voronoi(points)
voronoi_plot_2d(vor)
for i,p in enumerate(points):
    plt.text(p[0], p[1], '#%d' % i, ha='center')
plt.show()
"""


