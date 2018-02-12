import pandas as pd
import glob
import shutil
import argparse
import numpy as np


def bin_data(df, _binsize):
    
    df['stim_on'] = 0
    df.loc[abs(df['speed']) > 0, 'stim_on'] = 1
    df['synctime'] = df['Time'] - df.loc[df['stim_on'].argmax(), 'Time']
    df['timedelta'] = pd.to_timedelta(df['synctime'], unit='s')
    df.index = df['timedelta']
    
    return df.resample(_binsize).median()

def set_states(ang):
    for state in ['fwdmilling','bwdmilling','swarm','polarized']:
        ang[state] = 0
    ang.loc[(ang.polarization < 0.5) & (ang.dRotation > 0.5), 'fwdmilling'] = 1
    ang.loc[(ang.polarization < 0.5) & (ang.dRotation < -0.5), 'bwdmilling'] = 1
    ang.loc[(ang.polarization < 0.5) & (abs(ang.dRotation) < 0.5), 'swarm'] = 1
    ang.loc[(ang.polarization >= 0.5) & (abs(ang.dRotation) < 0.5), 'polarized'] = 1
    
    return ang
    
 
def plot_states(g, column):
    fig = plt.figure()
    ax1 = fig.add_subplot(141)
    ax2 = fig.add_subplot(142)
    ax3 = fig.add_subplot(143)
    ax4 = fig.add_subplot(144)
    plots = [ax1,ax2,ax3,ax4]
    for group, _data in g:
        label =  group + ' n=' + str(len(set(_data.trialID)))
        print label
        d = _data.groupby(_data.index)
        xs = d.mean()['synctime'].values
        for plot in plots: 
            ys = d.mean()[column].values
            error = d.sem()[column].values
            plt.fill_between(xs, ys-error, ys+error, alpha=0.2)
            plt.plot(d.mean()['synctime'], d.mean()[column], label=label)
            
    plt.xlabel('Time (seconds)')
    plt.ylabel(column + ' order')
    plt.legend()
    
    plt.show()
    return 
 
    
def plot(g, column):
    for group, _data in g:
        label =  group + ' n=' + str(len(set(_data.trialID)))
        print label
        d = _data.groupby(_data.index)
        xs = d.mean()['synctime'].values
        ys = d.mean()[column].values
        error = d.sem()[column].values
        plt.fill_between(xs, ys-error, ys+error, alpha=0.2)
        plt.plot(d.mean()['synctime'], d.mean()[column], label=label)
        
    plt.xlabel('Time (seconds)')
    plt.ylabel(column + ' order')
    plt.legend()
    
    plt.show()
    return


    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--save', type=str, required=True, 
                        help='provide a string for saving data')
    parser.add_argument('--dir', type=str, required=False, default = '/media/recnodes/kn-crec05,/media/recnodes/kn-crec06,/media/recnodes/kn-crec07',help='path to directory')
    parser.add_argument('--handle', type=str, required=False, default='_dotbot_', 
                        help='provide unique identifier (or comma-separated list) to select a subset of directories.')
    parser.add_argument('--exclude', type=str, required=False, default='EXCLUDENONE', 
                        help='provide unique identifier (or comma-separated list) to exclude a subset of directories.')
    parser.add_argument('--binsize', type=str, required=False, default='1s',
                        help='provide the bin size for pandas resampling, example "5s", "1H". Default is 1 second')
                
    args = parser.parse_args()
    
    HANDLES = args.handle.split(',')
    
    EXCLUDE = args.exclude.split(',')
    
    
    DIRECTORIES = args.dir.split(',')
    for x in range(len(DIRECTORIES)):
        if DIRECTORIES[x][-1] != '/':
            DIRECTORIES[x] += '/'

    BINSIZE = args.binsize


    DURATION = 400 # maximum time value for the experiment


    DATA = pd.DataFrame()

    for handle in HANDLES:
        for directory in DIRECTORIES:
            for fn in glob.glob(directory + '*' + handle + '*/track/frame_means_rotation_polarization.pickle'):
                gonogo = True
                for x in EXCLUDE:
                    if x in fn:
                        gonogo = False
                if gonogo:        
                    print 'processing: ', fn
                    try:
                        df = pd.read_pickle(fn)
                        expid, groupsize, _,  expdate, exptime = fn.rsplit('/',3)[1].split('_')
                        df = bin_data(df,  BINSIZE)
                        df['experiment'] = expid
                        df['groupsize'] = groupsize
                        df['date'] = expdate
                        df['startTime'] = exptime
                        df['coherenceGroup'] = df['coherence'].median()
                        df['trialID'] = expdate + '_' + exptime + '_' + str(df['coherence'].median())
                        
                        if '201712' in expdate:
                            if df['speed'].mean() > 0:
                                df['dRotation'] = df['dRotation']*-1.0
                        else:    
                            if df['dir'].mean() > 0:
                                df['dRotation'] = df['dRotation']*-1.0
                                
                        if df['speed'].mean() != 0:
                            DATA = pd.concat([DATA, df])
                        print '... OK'
                    except:
                        print '---------ERROR-------'
    print "----------FINISHED, saving-----------------"
    
    DATA = DATA.loc[DATA['synctime'] < DURATION, :]
    DATA = DATA.loc[DATA['synctime'] > -30, :]
    
    DATA['coherenceGroup'] = 10.0*np.round(DATA.coherenceGroup*10.0)
    DATA.index = DATA.index.round(BINSIZE)
    
    DATA.to_pickle('/media/recnodes/Dan_storage/compiled_datasets/' + args.save +  '.pickle')
    
    
    ang = DATA.loc[DATA['experiment'] == 'coherencetestangular', :]
    
    #colours = ['3d3d6bff','c70039ff','ffc300ff','57c785ff']
    

    
