#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib
#matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as manimation

FFMpegWriter = manimation.writers['ffmpeg']
metadata = dict(title='Movie Test', artist='Matplotlib',
                comment='Movie support!')
writer = FFMpegWriter(fps=40, metadata=metadata)

import numpy as np
import imgstore
import openpiv.process
import openpiv.validation
import openpiv.filters
import openpiv.scaling
import os
import cv2
import scipy.stats as stats

def downsample(array, n=3):
    """
    input is an np array of shape (z, x, y)
    returns an array of the median of axis z in groups of n (z/n, x, y)
    """
    slices = []
    for i in range(n):
        slices.append(array[range(i, int(len(array)/n)*n, n)])
    return np.median(np.array(slices), axis=0)    

def diff(p,q):
    """
    given two np arrays of type uint8 (common for images), 
    returns p minus q
    """
    return (p>q)*(p-q)+(p<q)*(q-p)
    
def sho(i):
    plt.imshow(i)
    plt.show()
    return
    
def createBackgroundImage(store, method='mode'):

    i, (CURRENT_FRAME, ts) = store.get_next_image()   
    firstframe=True
    for x in range(10):   
        
        skipFrames = 41#int(np.round(framecount/100))
        i, (f, t) = store.get_image(CURRENT_FRAME + skipFrames*x)
        if firstframe:
            img_array = i
            firstframe = False
        else:
            img_array = np.dstack((img_array, i))   

    if method == 'mode':
        bkgImg = stats.mode(img_array, axis=2)[0][:,:,0]
    elif method == 'mean':
        bkgImg = img_array.mean(axis=2)
    i, (CURRENT_FRAME, ts) = store.get_image(CURRENT_FRAME)
    return bkgImg


def makeSpots(img,):
    if len(img.shape) == 3:
        img = img[:,:,0]
    ret, contourImage = cv2.threshold(img.astype(np.uint8), 45, 255, cv2.THRESH_BINARY)
    _ , contours, hierarchy1 = cv2.findContours(contourImage, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    bodyCount = []
    matrix = np.zeros(img.shape)
    for cnt in contours:
        if cv2.contourArea(cnt) <=1000:
            if cv2.contourArea(cnt) >= 20:
                bodyCount.append(cnt)
    for c in bodyCount:
        M = cv2.moments(c)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        cv2.circle(matrix, (cx, cy), 1, (255,255,255), -1)
    print len(bodyCount)
    return matrix


def doPIV(img1, img2, size=5):

	u, v, sig2noise = openpiv.process.extended_search_area_piv( img1.astype(np.int32), img2.astype(np.int32), window_size=24*size, overlap=12*size, dt=0.02, search_area_size=64*size, sig2noise_method='peak2peak' )
	x, y = openpiv.process.get_coordinates( image_size=img1.shape, window_size=24*size, overlap=12*size )
	
	u, v, mask = openpiv.validation.sig2noise_val( u, v, sig2noise, threshold = 1.3 )
	u, v = openpiv.filters.replace_outliers( u, v, method='localmean', kernel_size=2)
	x, y, u, v = openpiv.scaling.uniform(x, y, u, v, scaling_factor = 100 )
	return x, y, u, v

def dropEmptySpaces(x,y,u,v):
    speed = np.sqrt(u**2+v**2)
    u[speed == 0] = np.nan
    v[speed == 0] = np.nan
    x[speed == 0] = np.nan
    y[speed == 0] = np.nan
    return x,y,u,v
    
def getRotatingVectorField(x, y, theta):
    """
    if theta is a single value, returns a circular rotating vector field (positive is clockwise).
    pass an array with x.shape for more complex warping
    """
    u = x*np.cos(theta) - y*np.sin(theta)
    v = x*np.sin(theta) + y*np.cos(theta)
    return {'x':x, 'y':y, 'u':u, 'v':v}

def getCentroid(x,y):
    return (x.mean(), y.mean())

def rotationalOrder(x,y,u,v):
    length = np.sqrt(u**2 + v**2)
    _u = u/length
    _v = v/length
    centroid = getCentroid(x,y)
    radius = np.sqrt((x-centroid[0])**2 + (y-centroid[1])**2)
    _x = x/radius
    _y = y/radius
    return np.cross(zip(_x.ravel(), _y.ravel()), 
                    zip(_u.ravel(), _v.ravel())).reshape(x.shape)

def divergence(x,y,u,v):
    dx = np.roll(x, -1, 1) - np.roll(x, 1, 1)
    du = np.roll(u, -1, 1) - np.roll(u, 1, 1)
    dy = np.roll(y, 1, 0) - np.roll(y, -1, 0)
    dv = np.roll(v, 1, 0) - np.roll(v, -1, 0)
    return du/dx + dv/dy

def vorticity(x,y,u,v):
    dx = np.roll(x, -1, 1) - np.roll(x, 1, 1)
    du = np.roll(u, -1, 1) - np.roll(u, 1, 1)
    dy = np.roll(y, 1, 0) - np.roll(y, -1, 0)
    dv = np.roll(v, 1, 0) - np.roll(v, -1, 0)
    return dv/dx - du/dy
              

def plot_quivers_and_save(x,y,u,v,colour,fn):
    fig = plt.figure(frameon=False)
    fig.set_size_inches(4,4)
    plt.Axes(fig, [0., 0., 1., 1.])  
    plt.quiver(x,y,u,v, colour, headwidth=5, scale=25)
    plt.clim(-5,5)
    plt.gca().set_aspect(1.0)
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
            hspace = 0, wspace = 0)
    plt.savefig(fn, dpi=300)
    plt.close('all')
    return
    
def plot_quivers_on_img(x,y,u,v,colour,img, fn):

    fig = plt.figure(frameon=False)
    fig.set_size_inches(4,4)
    plt.imshow(img, extent=[0,x.max()*(len(x)+1)/float(len(x)),0,y.max()*(len(y)+1)/float(len(y))])#Axes(fig, [0., 0., 1., 1.])  
    plt.quiver(x,y,u,v, abs(colour), cmap='Wistia', width=0.002, headwidth=4, headlength=5, scale=50)
    plt.clim(0,8)
    plt.gca().set_aspect(1.0)
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
            hspace = 0, wspace = 0)
    plt.savefig(fn, dpi=300)
    plt.close('all')
    return

def plot_sidebyside(x,y,u,v,colour,img, fn):
    img = img[104:3938, 104:3768]
    fig = plt.figure(frameon=False)
    fig.set_size_inches(8,4)
    ax = fig.add_subplot(1,2,1)
    plt.gca().set_axis_off()
    ax.imshow(img, extent=[0,x.max()*(len(x)+1)/float(len(x)),0,y.max()*(len(y)+1)/float(len(y))])#Axes(fig, [0., 0., 1., 1.])  
    ax2 = fig.add_subplot(1,2,2)
    QUIVER = ax2.quiver(x,y,u,v, abs(colour), cmap='gnuplot2', width=0.003, headwidth=4, headlength=5, scale=50)
    #plt.clim(0,8)
    #cbar = plt.colorbar(QUIVER, ax=ax2)
    #cbar.ax.set_ylabel('Vorticity', rotation=90)
    
    plt.gca().set_aspect(1.0)
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
            hspace = 0, wspace = 0)
    plt.savefig(fn, dpi=300)
    plt.close('all')
    return

def plotThemAll():
    for i in range(0,433):
        img, (f,t) = store.get_image(store.frame_min + 4001 + 3*i)
        plot_sidebyside(x,y,u[i],v[i],abs(vort[i]), img, OUTPUT_FILENAME +'/smoothed%06d.png'%(i))
        print "plotted: ", i
    return

def plot_temp(x,y,u,v,colour,img, CM):

    fig = plt.figure(frameon=False)
    fig.set_size_inches(4,4)
    plt.imshow(img, extent=[0,x.max()*(len(x)+1)/float(len(x)),0,y.max()*(len(y)+1)/float(len(y))])#Axes(fig, [0., 0., 1., 1.])  
    plt.quiver(x,y,u,v, abs(colour), cmap=CM, width=0.002, headwidth=4, headlength=5, scale=50)
    plt.clim(0,8)
    plt.gca().set_aspect(1.0)
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
            hspace = 0, wspace = 0)
    plt.show()#savefig(fn, dpi=300)
    plt.close('all')
    return



cdict = {
  'red'  :  ( (0.0, 0.25, .25), (0.02, .59, .59), (1., 1., 1.)),
  'green':  ( (0.0, 0.0, 0.0), (0.02, .45, .45), (1., .97, .97)),
  'blue' :  ( (0.0, 1.0, 1.0), (0.02, .75, .75), (1., 0.45, 0.45))
}

if __name__ == "__main__":
    import argparse
    import glob
    from utilities import *
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=False, default = '/home/dan/recnodes/recnode_2mfish/',help='path to directory')
    parser.add_argument('--handle', type=str, required=False, default='_dotbot_', 
                        help='provide unique identifier (or comma-separated list) to select a subset of directories.')
    parser.add_argument('--background', type=bool, required=False, default=False,
                        help="make true to generate a new background for the first video encountered")
    parser.add_argument('--startframe', type=int, required=False, default=0,
                        help="provide an integer of the first frame to be processed")
                
    args = parser.parse_args()
    
    HANDLE = args.handle.split(',')
    
    BKG_RULE = args.background
    
    DIRECTORIES = args.dir.split(',')
    for x in range(len(DIRECTORIES)):
        if DIRECTORIES[x][-1] != '/':
            DIRECTORIES[x] += '/'
    
    startframe = args.startframe

    for term in HANDLE:
        for DIR in DIRECTORIES:
            for vDir in glob.glob(DIR + '*' + term + '*.stitched'):
                OUTPUT_FILENAME = slashdir(vDir)
                if os.path.exists(OUTPUT_FILENAME + 'piv_complete'):
                    continue
                # LOAD VIDEO
                print "PROCESSING: ", OUTPUT_FILENAME
                STORE_FILENAME = slashdir(vDir) + 'metadata.yaml'
                store = imgstore.new_for_filename(STORE_FILENAME)
                
                img1 = np.zeros(store.image_shape)
                startframe = store.frame_min + startframe
                
                # LOAD OR CREATE A BACKGROUND IMAGE
                if BKG_RULE == False:
                    bkg = np.load('/home/dan/recnodes/Dan_storage/PIV/bkg_20181026_101202.npy' ) 
                elif BKG_RULE ==True:
                    bkg = createBackgroundImage(BKG_RULE, method='mode') #FIXME when tristan updates
                    date = '_'.join(vDir.split('/')[-1].split('.')[0].split('_')[-2:])
                    np.save('/home/dan/recnodes/Dan_storage/PIV/bkg_' + date + '.npy', bkg)
                    BKG_RULE=False

                # LOAD STORED DATA AND INITIALIZE DATA VARS
                if os.path.exists(OUTPUT_FILENAME + 'piv_u.npy'):
                    us = list(np.load(OUTPUT_FILENAME + 'piv_u.npy'))
                    vs = list(np.load(OUTPUT_FILENAME + 'piv_v.npy'))
                    vorts = list(np.load(OUTPUT_FILENAME + 'piv_vort.npy'))
                    startframe = us[-1][0]
                else:
                    us = []
                    vs = []
                    vorts = []
                firstframe = True   
                for i in range(startframe, store.frame_max-1):

                    if firstframe == True:
                        print "making image 1"
                        try:
                            img1, (_,_) = store.get_image(i)
                        except:
                            img1, (_,_) = store.get_next_image()
                        spots1 = makeSpots(diff(bkg,img1[:,:,0]))
                    
                    img2, (f,t)= store.get_next_image()
                    spots2 = makeSpots(diff(bkg,img2[:,:,0]))
                        
                    x,y,u,v = doPIV(spots1, spots2, size=20)
                    if firstframe == True:
                        np.save(OUTPUT_FILENAME + '/piv_x.npy', x)
                        np.save(OUTPUT_FILENAME + '/piv_y.npy', y)
                        firstframe = False
                    vort = vorticity(x,y,u,v)

                    us.append(np.append(np.array([f,t]),u.ravel()))
                    vs.append(np.append(np.array([f,t]),v.ravel()))
                    vorts.append(np.append(np.array([f,t]),vort.ravel()))

                    print "processed:", str(i)
                    if i%10 == 0:
                        
                        np.save(OUTPUT_FILENAME + 'piv_u.npy', us)
                        np.save(OUTPUT_FILENAME + 'piv_v.npy', vs)
                        np.save(OUTPUT_FILENAME + 'piv_vort.npy', vorts)
                    
                    spots1 = spots2  
                np.save(OUTPUT_FILENAME + 'piv_complete', x)     

                print "done"

