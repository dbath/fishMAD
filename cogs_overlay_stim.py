import pandas as pd
import numpy as np
import imgstore
from utilities import *
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection


def get_stim_data(MAIN_DIR):
       
    LOG_FN = '/media/recnodes/recnode_jolle2/dotbot_logs/dotbotLog_' + MAIN_DIR.split('/')[-2].rsplit('.',1)[0] + '.txt'
    log = pd.read_table(LOG_FN)
    log['Timestamp'] = log['Timestamp'] / 1000.0
    
    store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml')
    framelist = pd.DataFrame(store.get_frame_metadata())
    framelist.columns=['FrameNumber','Timestamp'] 

    g = log.groupby('comment')
    directions = {}
    for _name in g.groups.keys():
        g1 = g.get_group(_name)
        bar = framelist.merge(g1, how='outer')
        bar = bar.sort_values('Timestamp')
        bar['CX'].interpolate(inplace=True)
        bar['CY'].interpolate(inplace=True)
        framelist[_name + '_X'] = bar['CX']
        framelist[_name + '_Y'] = bar['CY']
        directions[_name] = g1.dir.mode()[0]
    
    return framelist, directions

def plot_on_image(img, data, fn):
    w, h, _ = ccw.shape
    fig, ax = plt.subplots(frameon=False)
    ax.imshow(img[104:3938, 104:3768], extent=[0,1280,0,1280], origin='upper')
    patches = []
    patches.append(Wedge((data.group1_X, data.group1_Y), 500, 0, 360 ))
    patches.append(Wedge((data.group2_X, data.group2_Y), 500, 0, 360  ))
    patches.append(Wedge((data.group3_X, data.group3_Y), 500, 0, 360  ))
    p = PatchCollection(patches, alpha=0.1)
    colours = np.array([0,100,50])
    p.set_array(colours)#['#30CC30','#CC3030','#30CC30']))
    ax.add_collection(p)
    ax.imshow(ccw, extent=[data.group1_X - w/2, data.group1_X + w/2, data.group1_Y - h/2, data.group1_Y +h/2],
                origin='upper')
    ax.imshow(cw, extent=[data.group2_X - w/2, data.group2_X + w/2, data.group2_Y - h/2, data.group2_Y +h/2],
                origin='upper')
    ax.imshow(ccw, extent=[data.group3_X - w/2, data.group3_X + w/2, data.group3_Y - h/2, data.group3_Y +h/2],
                origin='upper')
    
    ax.set_xlim(0,1280)
    ax.set_ylim(0,1280)
    
    plt.gca().set_aspect(1.0)
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
            hspace = 0, wspace = 0)
    plt.savefig(fn, dpi=300)
    plt.close('all')
    return
    

    
def fit_circle_2d(x, y, w=[]):
    
    A = np.array([x, y, np.ones(len(x))]).T
    b = x**2 + y**2
    
    # Modify A,b for weighted least squares
    if len(w) == len(x):
        W = np.diag(w)
        A = np.dot(W,A)
        b = np.dot(W,b)
    
    # Solve by method of least squares
    c = np.linalg.lstsq(A,b,rcond=None)[0]
    
    # Get circle parameters from solution c
    xc = c[0]/2
    yc = c[1]/2
    r = np.sqrt(c[2] + xc**2 + yc**2)
    return xc, yc, r    


MAIN_DIR = '/media/recnodes/recnode_2mfish/cogs3m_128_dotbot_20190116_121201.stitched'
MAIN_DIR = slashdir(MAIN_DIR) 
store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml')


ccw = plt.imread('/home/dan/fishMAD/arrow.png')
cw = np.flip(ccw, axis=0)

frames, dirs = get_stim_data(MAIN_DIR)

frames.fillna(1e9, inplace=True)


savedir = MAIN_DIR + 'annotated_video'
if not os.path.exists(savedir):
    os.mkdir(savedir)

listy = [-1]
for fn in glob.glob(savedir + '/*.png'):
    listy.append(int(fn.split('img')[-1].split('.')[0]))
    

for x in np.arange(max(listy)+1, frames.index.max()):
    data = frames.iloc[x]
    img, (f,t) = store.get_image(data.FrameNumber)
    fn = savedir + '/img%06d.png'%x
    plot_on_image(img, data, fn)

