import pandas as pd
import glob
import shutil
import argparse
import numpy as np
import stim_handling
import centroid_rotation
import matplotlib.pyplot as plt



def bin_data(df, _binsize):
    
    df['stim_on'] = 0
    df.loc[abs(df['speed']) > 0, 'stim_on'] = 1
    df['synctime'] = df['Time'] - df.loc[df['stim_on'].argmax(), 'Time']
    df['timedelta'] = pd.to_timedelta(df['synctime'], unit='s')
    df.index = df['timedelta']
    return df.resample(_binsize).mean()

def set_states(ang):
    for state in ['fwdmilling','bwdmilling','fwdFollowing','bwdFollowing','swarm','polarized']:
        ang[state] = 0
    ang.loc[(ang.polarization < 0.3) & (ang.dRotation > 0.5), 'fwdmilling'] = 1
    ang.loc[(ang.polarization < 0.3) & (ang.dRotation < -0.5), 'bwdmilling'] = 1
    ang.loc[(ang.polarization > 0.3) & (ang.cRotation > 0.35), 'fwdFollowing'] = 1
    ang.loc[(ang.polarization > 0.3) & (ang.cRotation < -0.35), 'bwdFollowing'] = 1
    ang.loc[(ang.polarization < 0.3) & (abs(ang.dRotation) < 0.5), 'swarm'] = 1
    ang.loc[(ang.polarization > 0.3) & (abs(ang.dRotation) < 0.5), 'polarized'] = 1
   
    return ang
    
 
def plot_states(g):
    states = ['fwdmilling','bwdmilling','fwdFollowing','bwdFollowing','fwd','bwd','swarm','polarized']
    fig, axs = plt.subplots(len(states),1)
    groupnum = 0
    for group, _data in g:
        label =  str(group) + ' n=' + str(len(set(_data.trialID)))
        print label
        d = _data.groupby(_data.index)
        xs = d.mean()['synctime'].values
        for x in range(0,len(states)): 
            plt.axes(axs[x])
            column = states[x]
            ys = d.mean()[column].values
            error = d.sem()[column].values
            plt.fill_between(xs, ys-error, ys+error, alpha=0.2, color=colours[groupnum])
            plt.plot(d.mean()['synctime'], d.mean()[column], label=label, color=colours[groupnum])
            plt.ylabel(column)
        groupnum +=1
    plt.xlabel('Time (seconds)')
    plt.legend()
    plt.show()
    return 


def plot_nice(g, _binsize='3s'):
    groupnum = 0
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    for group, _data in g:
        label =  str(group) + ' n=' + str(len(set(_data.trialID)))
        print label
        _data.index = _data.index.round(_binsize)
        d = _data.groupby(_data.index)
        xs = d.mean()['synctime'].values
        ys = (d.mean()['fwd'] - d.mean()['bwd']) / (d.mean()['fwd'] + d.mean()['bwd'] )
        ax1.plot(xs, ys, label=label, color=colours[groupnum])

        groupnum +=1
    ax1.set_ylim(-0.5,1.0)
    ax1.set_ylabel('Combined Rotation\n(Pc - Pe) / (Pe + Pc)')
    plt.xlabel('Time (seconds)')
    #plt.legend()
    plt.show()
    return 


def plot_CvE_adjusted(g):
    groupnum = 0
    fig = plt.figure()
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)
    for group, _data in g:
        label =  str(group) + ' n=' + str(len(set(_data.trialID)))
        print label
        d = _data.groupby(_data.index)
        xs = d.mean()['synctime'].values
        ys1 = (d.mean()['fwdmilling'] - d.mean()['bwdmilling']) / (d.mean()['fwdmilling'] + d.mean()['bwdmilling'] )
        ys2 = (d.mean()['fwdFollowing'] - d.mean()['bwdFollowing']) / (d.mean()['fwdFollowing'] + d.mean()['bwdFollowing'] )
        ys3 = (d.mean()['fwd'] - d.mean()['bwd']) / (d.mean()['fwd'] + d.mean()['bwd'] )
        ax1.plot(xs, ys1, label=label, color=colours[groupnum])
        ax2.plot(xs, ys2, label=label, color=colours[groupnum])
        ax3.plot(xs, ys3, label=label, color=colours[groupnum])

        groupnum +=1
    ax1.set_ylabel('Milling\n(Pc - Pe) / (Pe + Pc)')
    ax2.set_ylabel('Following\n(Pc - Pe) / (Pe + Pc)')
    ax3.set_ylabel('Combined Rotation\n(Pc - Pe) / (Pe + Pc)')
    plt.xlabel('Time (seconds)')
    plt.legend()
    plt.show()
    return 

def plot_CvCE(g):
    #fig, axs = plt.subplots(1,1)
    groupnum = 0
    fig = plt.figure()
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)
    for group, _data in g:
        label =  str(group) + ' n=' + str(len(set(_data.trialID)))
        print label
        d = _data.groupby(_data.index)
        xs = d.mean()['synctime'].values
        ys1 = (d.mean()['fwdmilling']) / (d.mean()['fwdmilling'] + d.mean()['bwdmilling'] )
        ys2 = (d.mean()['fwdFollowing']) / (d.mean()['fwdFollowing'] + d.mean()['bwdFollowing'] )
        ys3 = (d.mean()['fwd']) / (d.mean()['fwd'] + d.mean()['bwd'] )
        ax1.plot(xs, ys1, label=label, color=colours[groupnum])
        ax2.plot(xs, ys2, label=label, color=colours[groupnum])
        ax3.plot(xs, ys3, label=label, color=colours[groupnum])

        groupnum +=1
    ax1.set_ylabel('Milling\nPc / (Pe + Pc)')
    ax2.set_ylabel('Following\nPc / (Pe + Pc)')
    ax2.set_ylabel('Combined Rotation\nPc / (Pe + Pc)')
    plt.xlabel('Time (seconds)')
    plt.legend()
    plt.show()
    return 

def plotAdjustedRate(g, ax, CORRECT, _binsize='3s'):
    if CORRECT:
        column = 'fwd'
        title = 'Probability\nPc / (Pe + Pc)'
    else:
        column = 'bwd'
        title = 'Probability\nPe / (Pe + Pc)'
        
    groupnum = 0
    for group, _data in g:
        label =  str(group) + ' n=' + str(len(set(_data.trialID)))
        print label
        _data.index = _data.index.round(_binsize)
        d = _data.groupby(_data.index)
        xs = d.mean()['synctime'].values
        ys = (d.mean()[column]) / (d.mean()['fwd'] + d.mean()['bwd'] )
        ax.plot(xs, ys, label=label, color=colours[groupnum])
        ax.set_ylim(0.0,1.1)
        groupnum +=1
    ax.set_ylabel(title)
    plt.xlabel('Time (seconds)')
    return  
    
def plot(g, column):
    for group, _data in g:
        label =  str(group) + ' n=' + str(len(set(_data.trialID)))
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



def reBin(_df, _binsize):
    df = _df.copy()
    df[['groupsize','date','startTime','coherenceGroup']] = df[['groupsize','date','startTime','coherenceGroup']].astype(int)
    listy = list(set(df['trialID']))
    df['trialID'] = [listy.index(df.ix[k]['trialID']) for k in range(len(df))]
    df.index = df.index.round(_binsize)
    df = df.groupby(df.index).median()
    df['trialID'] = [listy[int(k)] for k in df['trialID']]
    return df

    
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


    DURATION = 700 # maximum time value for the experiment


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
                        ret, df = stim_handling.synch_coherence_with_rotation(fn.rsplit('/',2)[0])
                        if ret == 0:
                            print fn.split('/')[-3], 'logged stim does not match timestamps'
                            if os.path.exists(fn.rsplit('/')[0] + '/centroid_rotation.pickle'):
                                os.remove(fn.rsplit('/')[0] + '/centroid_rotation.pickle')
                            continue 
                        else:
                            #df = pd.read_pickle(fn)
                            expid, groupsize, _,  expdate, exptime = fn.rsplit('/',3)[1].split('_')
                            df['cRotation'] = centroid_rotation.get_centroid_rotation(fn.rsplit('/',2)[0], df, 2) 
                            df = bin_data(df,  BINSIZE)
                            df['experiment'] = expid
                            df['groupsize'] = groupsize
                            df['date'] = expdate
                            df['startTime'] = exptime
                            df['coherenceGroup'] = df['coherence'].median()
                            df['speedGroup'] = abs(df['speed']).max()
                            df['trialID'] = expdate + '_' + exptime + '_' + str(abs(df['speed']).max())
                            
                            if '201712' in expdate:
                                if df['speed'].min() >= 0:
                                    df['dRotation'] = df['dRotation']*-1.0
                                    df['cRotation'] = df['cRotation']*-1.0
                            else:    
                                if df['dir'].min() >= 0:
                                    df['dRotation'] = df['dRotation']*-1.0
                                    df['cRotation'] = df['cRotation']*-1.0   
                                      
                            df['cReversal'] = 0
                            if df.loc[df['synctime'] < 0, 'cRotation'].mean() < -0.35 :
                                df['cReversal'] = 1
                            elif df.loc[df['synctime'] < 0, 'cRotation'].mean() > 0.35 :
                                df['cReversal'] = -1
                            df['Reversal'] = 0
                            if df.loc[df['synctime'] < 0, 'dRotation'].mean() < -0.25 :
                                df['Reversal'] = 1
                            elif df.loc[df['synctime'] < 0, 'dRotation'].mean() > 0.25 :
                                df['Reversal'] = -1
                                   
                                   
                            df = set_states(df)
                            
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
    
    colours = ['#c70039ff','#57c785ff','#ffc300ff','#3d3d6bff']

    data = DATA.copy()
    #data = pd.read_pickle('/media/recnodes/Dan_storage/compiled_datasets/180310_coherencetestangular.pickle' )
    #data = set_states(data)
    data = data.loc[data['synctime'] < 300, :]
    data.loc[data['coherenceGroup'] ==00, 'coherenceGroup'] = 'low'
    data.loc[data['coherenceGroup'] ==10, 'coherenceGroup'] = 'low'
    data.loc[data['coherenceGroup'] ==20, 'coherenceGroup'] = 'low'
    data.loc[data['coherenceGroup'] ==30, 'coherenceGroup'] = 'low'
    data.loc[data['coherenceGroup'] ==40, 'coherenceGroup'] = 'moderate'
    data.loc[data['coherenceGroup'] ==50, 'coherenceGroup'] = 'moderate'
    data.loc[data['coherenceGroup'] ==60, 'coherenceGroup'] = 'moderate'
    data.loc[data['coherenceGroup'] ==70, 'coherenceGroup'] = 'moderate'
    data.loc[data['coherenceGroup'] ==80, 'coherenceGroup'] = 'high'
    data.loc[data['coherenceGroup'] ==90, 'coherenceGroup'] = 'high'
    data.loc[data['coherenceGroup'] ==100, 'coherenceGroup'] = 'high'    
    data.to_pickle('/media/recnodes/Dan_storage/compiled_datasets/' + args.save +  '_pooled.pickle')











def smoothline(x,y, N=300):
    xnew = np.linspace(y.min(),y.max(),N) #300 represents number of points to make between T.min and T.max
    c = [-1, 2, 0, -1]
    power_smooth = BSpline(x,y,2)    
    return xnew, power_smooth(xnew)

def fixIndex(df):
    df.index = np.log2(df.index.astype(int))
    df = df[df.index < 8].sort_index()
    return df


from scipy.interpolate import BSpline


def plot_success_vs_error(data):
    stim = data.loc[data['synctime'].between(120,200), :] 
    bwd = stim.loc[stim['groupsize'] == '128', 'fwd']
    fwd = stim.loc[stim['groupsize'] == '128', 'bwd']
    stim.loc[stim['groupsize'] == '128', 'fwd'] = fwd
    stim.loc[stim['groupsize'] == '128', 'bwd'] = bwd
    t = stim.groupby(['groupsize','coherenceGroup','trialID']).mean() #first take per-trial mean
    t['successRate'] = (t['fwd']) / (t['fwd'] + t['bwd']) #adjust for milling rate
    t['errorRate'] = (t['bwd']) / (t['fwd'] + t['bwd'])
    mean = t.groupby(['groupsize','coherenceGroup']).mean() 
    sem = t.groupby(['groupsize','coherenceGroup']).sem()

    successRate = fixIndex(mean.successRate.unstack())
    errorRate = fixIndex(mean.errorRate.unstack())
    successSEM = fixIndex(sem.successRate.unstack())
    errorSEM = fixIndex(sem.errorRate.unstack())

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.errorbar(successRate.index, successRate['low'], yerr=successSEM['low'], color='#57c785ff',  capthick=200, lw=4)
    ax1.errorbar(successRate.index, successRate['moderate'], yerr=successSEM['moderate'], color='#ffc300ff', capthick=200, lw=4)
    ax1.errorbar(successRate.index, successRate['high'], yerr=successSEM['high'], color='#c70039ff', capthick=200, lw=4)
    ax1.set_ylabel('Mean success rate\nP (correct) / P (milling)')
    ax1.set_xlabel('log2(Group Size)')

    plt.legend()
    plt.tight_layout()
    plt.show()
    return


def compareReversals(data):
    stim = data.loc[data['synctime'].between(0,180), :] 
    stim = stim.loc[stim['groupsize'] != '128']

    t = stim.groupby(['groupsize','coherenceGroup','trialID']).mean() #first take per-trial mean
    t['successRate'] = (t['fwd']) / (t['fwd'] + t['bwd']) #adjust for milling rate
    t['errorRate'] = (t['bwd']) / (t['fwd'] + t['bwd'])
    
    t.boxplot(column='successRate', by=['groupsize','Reversal'], rot=90, grid=False)

    mean = t.groupby(['cReversal','groupsize','coherenceGroup']).mean() 
    sem = t.groupby(['groupsize','coherenceGroup']).sem()

    successRate = fixIndex(mean.successRate.unstack())
    errorRate = fixIndex(mean.errorRate.unstack())
    successSEM = fixIndex(sem.successRate.unstack())
    errorSEM = fixIndex(sem.errorRate.unstack())    
        
def plotMeanVals(e,s):
    plt.errorbar(e.index, e['low'], yerr=s['low'], fmt='',  capthick=200)
    xs, ys = smoothline(e.index.values, e['low'])
    plt.plot(xs, ys, color='#57c785ff', linewidth=3)
    plt.errorbar(e.index, e['moderate'], yerr=s['moderate'], fmt='',  capthick=200)
    xs, ys = smoothline(e.index.values, e['moderate'])
    plt.plot(xs, ys, color='#ffc300ff', linewidth=3)
    plt.errorbar(e.index, e['high'], yerr=s['high'], fmt='',  capthick=200)
    xs, ys = smoothline(e.index.values, e['high'])
    plt.plot(xs, ys, color='#c70039ff', linewidth=3)
    plt.ylabel('Mean P (correct)')
    plt.xlabel('log2(Group Size)')
    plt.show()
    return

    
