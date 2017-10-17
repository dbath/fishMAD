import pandas as pd
import numpy as np
import glob
from matplotlib import cm 
import matplotlib.pyplot as plt
import cv2
import math
import os
import argparse

def plot_all(DIRECTORY):
    for fn in glob.glob(DIRECTORY + '/*.csv'):
        f = pd.read_csv(fn)
        plt.plot(f['X#centroid (cm)'], f['Y#centroid (cm)'])
    plt.show()
    return


def get_positions(DIRECTORY):
    df = pd.DataFrame()
    for fn in glob.glob(DIRECTORY + '/*.csv'):
        f = pd.read_csv(fn)
        tempdf = f[['frame', 'X#centroid (cm)','Y#centroid (cm)']]
        tempdf['ID'] = fn.split('fish')[-1].split('.')[0]
        tempdf.columns = ['frame','x','y', 'trackid']
        df = pd.concat([df, tempdf])
        df['frame'] = df['frame'].astype(int)
    df.replace(to_replace=np.inf, value=np.nan, inplace=True)
    return df

def get_velocities(DIRECTORY):
    df = pd.DataFrame()
    for fn in glob.glob(DIRECTORY + '/*.csv'):
        f = pd.read_csv(fn)
        tempdf = f[['frame', 'VX#centroid (cm/s)',  'VY#centroid (cm/s)']]
        tempdf['ID'] = fn.split('fish')[-1].split('.')[0]
        tempdf.columns = ['frame','vx','vy', 'trackid']
        df = pd.concat([df, tempdf])
    df['frame'] = df['frame'].astype(int)
    df.replace(to_replace=np.inf, value=np.nan, inplace=True)
    return df    

def get_data(DIRECTORY):
    df = pd.DataFrame()
    i = 0
    for fn in glob.glob(DIRECTORY + '/*.csv'):
        i +=1
        f = pd.read_csv(fn)
        tempdf = f[['frame', 'X#centroid (cm)','Y#centroid (cm)', 'VX#centroid (cm/s)',  'VY#centroid (cm/s)']]
        tempdf['ID'] = fn.split('fish')[-1].split('.')[0]
        tempdf.columns = ['frame','x','y','vx','vy', 'trackid']
        df = pd.concat([df, tempdf])
        if i%500 == 0:
            print "processed track number :", i
            df.to_pickle(DIRECTORY_MAIN + '/data.pickle')
    df['frame'] = df['frame'].astype(int)
    df.replace(to_replace=np.inf, value=np.nan, inplace=True)
    df.to_pickle(DIRECTORY_MAIN + '/data.pickle')
    return df  

def get_centroid(arr):
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    return sum_x/length, sum_y/length

def get_colours(L):
    """pass an integer (L), returns a list of length (L) with colour codes"""
    foo = cm.hsv(np.linspace(0, 1, L))
    np.random.shuffle(foo)
    return foo

def angle_from_vertical(point1, point2):
    """
    RETURNS A VALUE IN DEGREES BETWEEN 0 AND 360, WHERE 0 AND 360 ARE NORTH ORIENTATION.
    """
    x = point1[0] - point2[0]
    y = point1[1] - point2[1]
    return 180.0 + math.atan2(x,y)*180.0/np.pi


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=True,
                        help='path to main directory')
    parser.add_argument('--makevid', type=bool, required=False, default=False,
                        help='make true to make a video')
    args = parser.parse_args()
    MAKEVID = args.makevid
    DIRECTORY_MAIN = args.dir
    
    if DIRECTORY_MAIN[-1] == '/':
        DIRECTORY_MAIN = DIRECTORY_MAIN[:-1]
    if MAKEVID:
        for vid in glob.glob(DIRECTORY_MAIN + '/00*.mp4'):
            vidfile = vid
        if not os.path.exists(DIRECTORY_MAIN + '/annotated_vid'):
            os.makedirs(DIRECTORY_MAIN + '/annotated_vid')
        
    #positions = get_positions(DIRECTORY_MAIN + '/fishdata' )
    print 'got positions'
    #velocities = get_velocities(DIRECTORY_MAIN + '/fishdata' )
    print 'got velocities'
    #colourlist = get_colours(len(set(positions['trackid'])))
    #colourmap = dict(zip(list(set(positions['trackid'])), colourlist))

    if not os.path.exists(DIRECTORY_MAIN + '/data.pickle' ):
        posVel = get_data(DIRECTORY_MAIN + '/fishdata' )
    else:
        posVel = pd.read_pickle(DIRECTORY_MAIN + '/data.pickle' )
    #fpos = positions.groupby(['frame'])
    #fvel = velocities.groupby(['frame'])
    #posVel = positions.merge(velocities, on=['frame','trackid'])
    
    f = posVel.groupby(['frame'])
    """
    #Plot coloured dots on graph:    
    for frame, data in f:
        colours = [colourmap[k] for k in set(data.trackid)]
        plt.scatter(data['x'],data['y'], color=colours)
        plt.xlim(0,128)
        plt.ylim(0,128)
        plt.savefig('/home/dbath/Documents/tracking_tests/fishtracker/positions_by_frame/%03d.png'%(frame) , bbox_inches='tight', pad_inches=0)
        plt.close('all')
        
    #Plot dots on video:

    vid = cv2.VideoCapture('/home/dbath/Documents/tracking_tests/000279.mp4')   
    lastframe = -1
    for frame, data in fpos:
        if frame != (lastframe +1):
            vid.set(1, int(frame))
        lastframe = frame
        ret, img = vid.read()
        #colours = [colourmap[k] for k in set(data['trackid'])]
        
        #print len(colours), len(data)
        #keysvals = [k for k in data['trackid']]
        plt.figure(figsize=(2.048, 2.048), dpi=100)
        plt.imshow(img)
        #plt.scatter(xs,ys, color=colours, s=1)
        #plt.scatter(16.0*data['x'].values,16.0*data['y'].values, color=colours, s=1)
        plt.scatter(16.0*data['x'].values,16.0*data['y'].values, color='#00FF00', s=0.2, linewidth=0)

        a=plt.gca()
        a.set_frame_on(False)
        a.set_xticks([]); a.set_yticks([])
        plt.axis('off')
        plt.xlim(0,2048)
        plt.ylim(0,2048)
        plt.tight_layout()
        plt.savefig('/home/dbath/Documents/tracking_tests/fishtracker/fish_with_dots/%03d.png'%(frame) , bbox_inches='tight', pad_inches=0, dpi=1000)
        plt.close('all')
    """

            

        
    frame_stats = pd.DataFrame()
    if MAKEVID:
        vid = cv2.VideoCapture(vidfile)   
        lastframe = -1
    #find the centroid in each frame:
    for i, data in f:
        data = data.dropna()
        points = np.array(zip(data['x'], data['y']))
        centroid = get_centroid(points)
        try:
            data['angleOfMotion'] = [ angle_from_vertical((0,0),np.array(data.loc[k, ['vx','vy']])) for k in data.index]
        except:
            print data[0:5]
        data['angleFromCentroid'] = [angle_from_vertical(np.array(data.loc[k, ['x','y']]), centroid) for k in data.index]
        data['angleToCentroid'] = data['angleFromCentroid'] - data['angleOfMotion']
        data.loc[data['angleToCentroid'] >= 180, 'angleToCentroid'] -= 360.0
        data.loc[data['angleToCentroid'] <= -180, 'angleToCentroid'] += 360.0
        
        
        frame_stats.loc[i, 'cx'] = centroid[0]
        frame_stats.loc[i, 'cy'] = centroid[1]
        frame_stats.loc[i, 'medianAngle'] = data['angleToCentroid'].median()
        frame_stats.loc[i, 'meanAngle'] = data['angleToCentroid'].mean()
        frame_stats.loc[i, 'stdAngle'] = data['angleToCentroid'].std()
        
        if i%100 == 0:
            print "processed frame number :", i
            frame_stats.to_pickle(DIRECTORY_MAIN + '/frame_stats.pickle')
        
        if MAKEVID:
            if i != (lastframe +1):
                vid.set(1, int(i))
            lastframe = i
            ret, img = vid.read()
            
            fig = plt.figure(figsize=(2.048, 2.304), dpi=100)
            ax1 = plt.subplot2grid((9,8), (0,0), colspan=8, rowspan=8)
            fig.add_axes(ax1)
            plt.imshow(img)
            plt.plot(16.0*centroid[0], 16.0*centroid[1], marker='*', markersize=3, c="#FFFF00", linewidth=0.01)
            a=plt.gca()
            ax1.set_frame_on(False)
            ax1.set_xticks([]); ax1.set_yticks([])
            plt.axis('off')
            plt.xlim(0,2048)
            plt.ylim(0,2048)
              
            ax2 = plt.subplot2grid((9,8), (8,0), colspan=8, rowspan=1)
            fig.add_axes(ax2)
            
            plt.hist(data['angleToCentroid'].values, bins=180, normed=True, linewidth=0)
            ax2.set_xlabel('Degrees', fontsize=2, labelpad=0.2)
            #ax2.set_ylabel('Frequency', fontsize=2)
            ax2.set_xlim(-210, 210)
            ax2.set_xticks([-180, -90, 0, 90, 180])
            ax2.tick_params(axis='x', which='major', labelsize=2, length=1, width=0.1)
            ax2.tick_params(axis='y', which='major', labelsize=2, length=0, width=0.0)
            ax2.set_ylim(0,0.05)  
            ax2.set_yticks([])
            for axis in ['top','right', 'left']:   
                ax2.spines[axis].set_visible(False)
            for axis in ['top','bottom','left']:
                ax2.spines[axis].set_linewidth(0.1)
            for axis in ['right', 'left']:   
                ax2.spines[axis].set_visible(False)
            #ax2.yaxis.set_ticks_position('left')
            ax2.xaxis.set_ticks_position('bottom') 
            
            fig.tight_layout()  
            fig.subplots_adjust(wspace=0.00, top=1.0, bottom=0)
            fig.subplots_adjust(hspace=0.00)
            plt.savefig(DIRECTORY_MAIN + '/annotated_vid/%03d.png'%(i) , bbox_inches='tight', pad_inches=0, dpi=1000)
            plt.close('all')    

    frame_stats.to_pickle(DIRECTORY_MAIN + '/frame_stats.pickle')
    
    fig = plt.figure()#figsize=(2, 2), dpi=100)
    ax1 = plt.subplot2grid((2,1), (0,0))
    fig.add_axes(ax1)
    plt.hist(frame_stats['medianAngle'], bins=80, normed=True, color='#CC3030', linewidth=0.1)
    ax1.set_xlim(-210, 210)
    ax1.set_xlabel('Median Angle to Centroid')
    ax1.set_xticks([-180, -90, 0, 90, 180]) 
    ax1.set_yticks([])
    ax1.xaxis.set_ticks_position('bottom') 


    ax2 = plt.subplot2grid((2,1), (1,0))
    fig.add_axes(ax2)
    plt.hist(frame_stats['stdAngle'], bins=80, normed=True, color='#30CC30', linewidth=0.1)
    ax2.set_xlim(0, 180)
    ax2.set_xlabel('Std. Deviation of Angle to Centroid')
    ax2.set_yticks([])
    ax2.xaxis.set_ticks_position('bottom') 

    for axis in ['bottom','left']:
        ax1.spines[axis].set_linewidth(0.6)
        ax2.spines[axis].set_linewidth(0.6)
    for axis in ['top','right']:   
        ax1.spines[axis].set_visible(False)
        ax2.spines[axis].set_visible(False)
    plt.title(DIRECTORY_MAIN.split('/')[-1])

    fig.tight_layout()  
    #fig.subplots_adjust(wspace=0.20, top=1.0, bottom=0)
    #fig.subplots_adjust(hspace=0.20)
    plt.savefig(DIRECTORY_MAIN + '/statistics.svg' , bbox_inches='tight', pad_inches=0)#, dpi=1000)
