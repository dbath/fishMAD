import numpy as np
import matplotlib.pyplot as plt
from shapely.ops import polygonize,unary_union
from shapely.geometry import LineString, MultiPolygon, MultiPoint, Point
from scipy.spatial import Voronoi



points = [[-30.0, 30.370371], [-27.777777, 35.925926], [-34.444443, 58.51852], [-2.9629631, 57.777779], [-17.777779, 75.185181], [-29.25926, 58.148151], [-11.111112, 33.703705], [-11.481482, 40.0], [-27.037037, 40.0], [-7.7777777, 94.444443], [-2.2222223, 122.22222], [-20.370371, 106.66667], [1.1111112, 125.18518], [-6.2962961, 128.88889], [6.666667, 133.7037], [11.851852, 136.2963], [8.5185184, 140.74074], [20.370371, 92.962959], [17.777779, 114.81482], [12.962962, 97.037041], [13.333334, 127.77778], [22.592592, 120.37037], [16.296295, 127.77778], [11.851852, 50.740742], [20.370371, 54.814816], [19.25926, 47.40741], [32.59259, 122.96296], [20.74074, 130.0], [24.814816, 84.814819], [26.296295, 91.111107], [56.296295, 131.48149], [60.0, 141.85185], [32.222221, 136.66667], [53.703705, 147.03703], [87.40741, 196.2963], [34.074074, 159.62964], [34.444443, -2.5925925], [36.666668, -1.8518518], [34.074074, -7.4074073], [35.555557, -18.888889], [76.666664, -39.629627], [35.185184, -37.777779], [25.185184, 14.074074], [42.962959, 32.962963], [35.925926, 9.2592592], [52.222221, 77.777779], [57.777779, 92.222221], [47.037041, 92.59259], [82.222221, 54.074074], [48.888889, 24.444445], [35.925926, 47.777779], [50.740742, 69.259254], [51.111111, 51.851849], [56.666664, -12.222222], [117.40741, -4.4444447], [59.629631, -5.9259262], [66.666664, 134.07408], [91.481483, 127.40741], [66.666664, 141.48149], [53.703705, 4.0740738], [85.185181, 11.851852], [69.629631, 0.37037039], [68.518517, 99.259262], [75.185181, 100.0], [70.370369, 113.7037], [74.444443, 82.59259], [82.222221, 93.703697], [72.222221, 84.444443], [77.777779, 167.03703], [88.888893, 168.88889], [73.703705, 178.88889], [87.037041, 123.7037], [78.518517, 97.037041], [95.555557, 52.962959], [85.555557, 57.037041], [90.370369, 23.333332], [100.0, 28.51852], [88.888893, 37.037037], [87.037041, -42.962959], [89.259262, -24.814816], [93.333328, 7.4074073], [98.518517, 5.185185], [92.59259, 1.4814816], [85.925919, 153.7037], [95.555557, 154.44444], [92.962959, 150.0], [97.037041, 95.925919], [106.66667, 115.55556], [92.962959, 114.81482], [108.88889, 56.296295], [97.777779, 50.740742], [94.074081, 89.259262], [96.666672, 91.851852], [102.22222, 77.777779], [107.40741, 40.370369], [105.92592, 29.629629], [105.55556, -46.296295], [118.51852, -47.777779], [112.22222, -43.333336], [112.59259, 25.185184], [115.92592, 27.777777], [112.59259, 31.851852], [107.03704, -36.666668], [118.88889, -32.59259], [114.07408, -25.555555], [115.92592, 85.185181], [105.92592, 18.888889], [121.11111, 14.444445], [129.25926, -28.51852], [127.03704, -18.518518], [139.25926, -12.222222], [141.48149, 3.7037036], [137.03703, -4.814815], [153.7037, -26.666668], [-2.2222223, 5.5555558], [0.0, 9.6296301], [10.74074, 20.74074], [2.2222223, 54.074074], [4.0740738, 50.740742], [34.444443, 46.296295], [11.481482, 1.4814816], [24.074076, -2.9629631], [74.814819, 79.259254], [67.777779, 152.22223], [57.037041, 127.03704], [89.259262, 12.222222]]



points = np.array(points)



vor = Voronoi(points)


lines = [
    LineString(vor.vertices[line])
    for line in vor.ridge_vertices if -1 not in line
]

convex_hull = MultiPoint([Point(i) for i in points]).convex_hull.buffer(2)
result = MultiPolygon(
    [poly.intersection(convex_hull) for poly in polygonize(lines)])
result = MultiPolygon(
    [p for p in result]
    + [p for p in convex_hull.difference(unary_union(result))])

plt.plot(points[:,0], points[:,1], 'ko')
for r in result:
    plt.fill(*zip(*np.array(list(
        zip(r.boundary.coords.xy[0][:-1], r.boundary.coords.xy[1][:-1])))),
        alpha=0.4)
plt.show()

###############################################################################

#find all points that share an edge:
from scipy.spatial import Delaunay
from collections import defaultdict
import itertools

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



def plot_delaunay(tri, points, trackIDs, xlim=(0,400), ylim=(0,400), fig=None, ax=None):
    """
    tri: an object of scipy.spatial.Delaunay made from points eg (tri = Delaunay(points))
    points: x and y positions to plot in format: np.array(zip(data[XPOS],data[YPOS]))
    trackIDs: string values to label points, in same order as 'points'
    """
    if fig==None:
        fig = plt.figure()
    if ax== None:
        ax = fig.add_subplot(111)
    plt.triplot(points[:,0], points[:,1], tri.simplices, color='#00FF00FF')
    plt.plot(points[:,0], points[:,1], 'o', color='#FFFF00FF')
    for i,p in enumerate(points):
        plt.text(p[0], p[1], trackIDs.iloc[i], ha='center')
    
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

    for key in sorted(neiList.iterkeys()):
        neighbourhoodWatch(data.iloc[key], data.iloc[list(neiList[key])].reset_index())
        
    return 



def doit(fbf):
    
    f = fbf.groupby(['frame'])
    for i, data in f:
        data = data.replace(to_replace=np.inf, value=np.nan)
        


from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
vor = Voronoi(points)
voronoi_plot_2d(vor)
for i,p in enumerate(points):
    plt.text(p[0], p[1], '#%d' % i, ha='center')
plt.show()



