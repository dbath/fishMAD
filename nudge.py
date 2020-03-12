from utilities import *
import stim_handling as stims
import pandas as pd
import numpy as np
import imgstore




def sync_by_initiation(df, log, store, ID, col='nudge'):
    """
    pass a df with stim information
    returns the df with rotation values adjusted for direction so rotation of new stim is positive
    """

    alignPoints = list(log[log.comment == 'initiate']['Timestamp'].values) 

    if len(alignPoints) == 0:
        print("found no stim start frames - aborting")
        return 0, pd.DataFrame()
        
    foo = stims.get_frame_metadata(df, store)
    bar = foo.merge(log, how='outer') 
    bar = bar.sort_values('Timestamp')  #integrate log data with tracking data
    bar = bar.fillna(method='ffill')  #forward fill data from log to tracking data
    bar = bar.sort_values('Timestamp')    
    XLIM = (-5,11)
    bar.reset_index(inplace=True)
    trials = pd.DataFrame()
    trialID = 0    
    for i in alignPoints:
        data = bar.loc[bar['Timestamp'].between(i+XLIM[0], i+XLIM[1]),:].copy()
        for column in data.columns:
            if ('n_dRotation' in column) or ('centroidRotation' in column): #what a silly hack to catch all the different names for rotation. lazy
                data[column] = data[column]*np.sign(data['dir'].mean())
        data['syncTime'] = pd.to_timedelta(data['Timestamp']-i,'s') 
        data['trialID'] = ID + '_' + str(trialID)
        data['date'] = ID.split('_')[0]   
        data['startTime'] = ID.split('_')[1] 
        data['nudgeDir'] = float(data['theta'].max()) #make categorical for sorting
        data['divergence'] = float(data['divergence'].max())  #make categorical for sorting
        trialID += 1
        trials = pd.concat([trials, data], axis=0)
    return 1, trials

def cosine_similarity(ax,ay,bx,by):
    s = ax*bx +ay*by
    la = np.sqrt(ax**2 + ay**2)
    lb = np.sqrt(bx**2 + by**2)
    return s/(la*lb)


def hists(grouped,ax, col='dNudgeDir'):
    #delete me. i'm for figuring stuff out
    times  = [-4500,-3000,-1500,0,1500,3000,4500,6000,7500]
    cs = create_colourlist(len(times)-1, cmap='viridis')
    cs[:,-1]*=0.15  #set alpha
    for i in range(len(times)-1):
        data = grouped[grouped.syncTime.between(np.timedelta64(times[i], 'ms'), np.timedelta64(times[i+1],'ms'))]  
        ax.hist(data[col], bins=200, color=cs[i], label=str(times[i])+':'+str(times[i+1])+'s')
    plt.legend()
    return ax

def ts_hist(data,ax, col='dTheta'):
    #delete me. i'm for figuring stuff out
    data['seconds'] = [x.total_seconds() for x in data.syncTime]
    plt.hist2d(data['seconds'], data['dTheta'], bins=100)
    return ax


def compile_images(handle):
    divs = ['0.0','0.13','0.26','0.39','0.52','0.65','0.79','0.92','1.05','1.18','1.31','1.44','1.57']
    xbins = np.linspace(-5,11,128)   
    ybins = np.linspace(-1.0*np.pi, np.pi, 120)  
    fig = plt.figure()
    for div in divs:
        imglist = []
        filelist = []
        ax = fig.add_subplot(3,5,1+divs.index(div))
        for fn in glob.glob('/media/recnodes/recnode_2mfish/*' + handle + '*.stitched/track/dTheta_v_Time_' + div +'_*.npy'):
            filelist.append(fn.split('/')[-1]) 
            imglist.append(np.load(fn)) 
        d = np.stack(imglist)
        summimage = d.sum(axis=0).T
        ax.imshow(summimage, extent=[xbins.min(), xbins.max(), ybins.min(), ybins.max()], origin='lower')
        ax.set_title(div+ ', N= '+ str(len(filelist)))
    return fig

if __name__ == "__main__":
    import glob
    import argparse
    import os
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--handle', type=str, required=False, default='', 
                        help='provide unique identifier (or comma-separated list) to select a subset of directories.')


                
    args = parser.parse_args()
    
    
    #HANDLE = args.handle.split(',')
    filelist = []
    for MAIN_DIR in glob.glob('/media/recnodes/recnode_2mfish/nudge3m_128*.stitched'):
        print(MAIN_DIR)
        MAIN_DIR = slashdir(MAIN_DIR)
        ID = MAIN_DIR.split('/')[-2].split('_',3)[-1].split('.')[0]  
        if not os.path.exists(MAIN_DIR + 'track/frameByFrameData.pickle'):
            continue
        #if len([n for n in glob.glob(MAIN_DIR + 'track/dTheta_v_Time_1.57_*.npy') if os.path.exists(n)]) >0:
        #    continue
        log = stims.get_logfile(MAIN_DIR)
        store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml')

        fbf = pd.read_pickle(MAIN_DIR + 'track/frameByFrameData.pickle')
        if len(fbf.shape) == 1:
            fbf = joblib.load(MAIN_DIR + 'track/frameByFrameData.pickle')
            
        if 'header' in fbf.columns:
            fbf = fbf.drop(columns=['header'])
            

        fbf = fbf.loc[fbf[XPOS].notnull(), :]
        fbf = fbf.loc[fbf[YPOS].notnull(), :]
        fbf.loc[:,'uVX'] = fbf.loc[:,XVEL] / fbf.loc[:,SPEED]
        fbf.loc[:,'uVY'] = fbf.loc[:,YVEL] / fbf.loc[:,SPEED]

        ret, df = sync_by_initiation(fbf, log, store, ID)
        df.loc[df['nudgeDir']> np.pi, 'nudgeDir'] -= 2*np.pi
        df['velTheta'] = np.arctan2(df['uVY'], df['uVX'])     
        #df.loc[df['velTheta']<0, 'velTheta'] += 2*np.pi  
        df['dTheta'] = df['velTheta'] - df['nudgeDir']  
        df.loc[df['dTheta']> np.pi, 'dTheta'] -= 2*np.pi 
        df.loc[df['dTheta']< -1.0*np.pi, 'dTheta'] += 2*np.pi         
        """
        df['uNX'] = np.cos(df['nudgeDir']) 
        df['uNY'] = np.sin(df['nudgeDir'])  
        df['dX'] = df['uVX'] - df['uNX']  
        df['dY'] = df['uVY'] - df['uNY']   
        df['dNudgeDir'] = np.sqrt(df['dX']**2 + df['dY']**2)
        df['cosNudgeDir'] = np.cos(df['dNudgeDir'])
        """
        g = df.groupby('divergence')  

        xbins = np.linspace(-5,11,128)   
        ybins = np.linspace(-1.0*np.pi, np.pi, 120)   

        for div, dat in g: 
            seconds = np.array([x.total_seconds() for x in dat.syncTime])
            img, _, _ = np.histogram2d(seconds, np.array(dat['dTheta']), bins=(xbins, ybins))
            np.save(MAIN_DIR + 'track/dTheta_v_Time_' + str(np.around(div, 2)) +'_'+ dat.iloc[0]['trialID'] + '.npy', img)
            fig, ax = plt.subplots(figsize=(8,7))
            ax.imshow(img.T, extent=[xbins.min(), xbins.max(), ybins.min(), ybins.max()], origin='lower') 
            ax.set_ylabel('Angular deviation from stimulus direction (rad)')  
            ax.set_xlabel('Time (seconds) since stimulus onset')      
            plt.savefig(MAIN_DIR + 'track/dTheta_v_Time_' + str(np.around(div, 2)) +'_'+ dat.iloc[0]['trialID'] +'.png', bbox_inches='tight', pad_inches=0)    
            plt.close('all')



        """
        colourlist = create_colourlist(len(g.groups), cmap='viridis')
        ITER = 0
        #cosim_med = {}
        for d, data in g: 
            data.index = data.syncTime 
            #data['cosine_similarity'] = [cosine_similarity(i[1].uVX,i[1].uVY, i[1].uNX, i[1].uNY) for i in data.iterrows()]
            #cosim_med[d] = data['cosine_similarity']
            t = data.resample('25ms').median() 
            plt.plot(t.dTheta, label=d, color=colourlist[ITER]) 
            ITER +=1
            
        plt.legend()

        """



