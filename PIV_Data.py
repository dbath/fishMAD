import matplotlib.pyplot as plt
import numpy as np
import imgstore
import pandas as pd

from utilities import *


class PIV_Data(object):
    def __init__(self, directory):
        self.DIR = directory
        self.u_raw = np.load(directory + '/piv_u.npy')
        self.v_raw = np.load(directory + '/piv_v.npy')
        self.x = np.load(directory + '/piv_x.npy')
        self.y = np.load(directory + '/piv_y.npy')
        self.radius = self.get_radius_matrix()
        self.vort_raw = np.load(directory + '/piv_vort.npy')
        self.shape = self.x.shape
        
        self.store = imgstore.new_for_filename(directory+'/metadata.yaml')

    def get_frame_data(self, framenum):
        u = np.reshape(self.u_raw[framenum][2:],(self.shape))
        v = np.reshape(self.v_raw[framenum][2:],(self.shape))
        vort = np.reshape(self.vort_raw[framenum][2:],(self.shape))
        return u,v,self.x,self.y,vort

    def get_frame_count(self):
        return self.store.frame_count

    def plot_quivers_on_img(self, framenumber, filename):
        
        img, (f,t) = self.store.get_image(self.store.frame_min + framenumber)
        
        u,v,x,y,vort = self.get_frame_data(framenumber)
                
        fig = plt.figure(frameon=False)
        fig.set_size_inches(4,4)
        plt.imshow(img, extent=[0,x.max()*(len(x)+1)/float(len(x)),0,y.max()*(len(y)+1)/float(len(y))])
        plt.quiver(x,y,u,v, abs(vort), cmap='Wistia', width=0.002, headwidth=4, headlength=5, scale=50)
        plt.clim(0,8)
        plt.gca().set_aspect(1.0)
        plt.gca().set_axis_off()
        plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                hspace = 0, wspace = 0)
        plt.savefig(filename, dpi=300)
        plt.close('all')
        return

    def plot_sidebyside(self, framenumber, outstore, setup=False):
        
        img, (f,t) = self.store.get_image(self.store.frame_min + framenumber)
        
        u,v,x,y,vort = self.get_frame_data(framenumber)

        img = img[104:3938, 104:3768]
        fig = plt.figure(frameon=False)
        fig.set_size_inches(8,4)
        fig.set_dpi(300)
        ax = fig.add_subplot(1,2,1)
        plt.gca().set_axis_off()
        ax.imshow(img, extent=[0,x.max()*(len(x)+1)/float(len(x)),0,y.max()*(len(y)+1)/float(len(y))])
        ax2 = fig.add_subplot(1,2,2)
        QUIVER = ax2.quiver(x,y,u,v, abs(vort), cmap='gnuplot2', width=0.003, headwidth=4, headlength=5, scale=50)

        plt.gca().set_aspect(1.0)
        plt.gca().set_axis_off()
        plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                hspace = 0, wspace = 0)
        
        fig.canvas.draw()
        drawn = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
        drawn = drawn.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        if setup==True:
            return drawn.shape
        else:
            outstore.add_image(drawn, f, t)
            #plt.savefig(filename, dpi=300)
            plt.close('all')
            return   drawn
            
    def get_radius_matrix():
        Rx = self.x - np.median(self.x[0])
        Ry = self.y - self.y[len(self.y)/2] 
        return np.sqrt(Rx**2 + Ry**2)

    def sync_stim_with_data(self, data):
        r = pd.DataFrame(data)
        MAIN_DIR = slashdir(self.directory)
        LOG_FN = '/media/recnodes/recnode_jolle2/dotbot_logs/dotbotLog_' + MAIN_DIR.split('/')[-2].rsplit('.',1)[0] + '.txt'

        framelist = pd.DataFrame(self.store.get_frame_metadata())
        framelist.columns=['FrameNumber','Timestamp'] 

        log = pd.read_table(LOG_FN)
        log.loc[:,'Timestamp'] /=  1000.0

        bar = framelist.merge(log, how='outer') 
        bar = bar.sort_values('Timestamp') 
        bar['coh'] = bar['coh'].fillna(method='ffill')
        bar['coherence'] = bar['coh']#silly lazy hack
        bar['speed'] = bar['speed'].fillna(method='ffill').fillna(0)
        bar['dir'] = bar['dir'].fillna(method='ffill').fillna(0)
        bar.loc[:,'Time'] = (bar.loc[:,'Timestamp'] - bar.loc[0,'Timestamp'])
        if bar.iloc[5].Timestamp - bar.iloc[0].Timestamp > 10: #check if log overlaps with track data
            return 0, bar
        else:    
            return 1, bar  


if __name__ == "__main__":
        
    vidfile = '/media/recnodes/recnode_2mfish/reversals3m_1024_dotbot_20181025_123202.stitched'
    data = PIV_Data(vidfile)
    import os
    if not os.path.exists(vidfile+'/sidebyside'):
        os.makedirs(vidfile+'/sidebyside')
    imgshape = data.plot_sidebyside(0, "asdf", setup=True)    
    out = imgstore.new_for_format( 'avc1/mp4', mode='w', 

                basedir=vidfile+'/sidebyside',
                imgshape=imgshape,
                imgdtype='uint8',
                chunksize=500)        
    for n in range(data.get_frame_count()):
        data.plot_sidebyside(n, out)
             
