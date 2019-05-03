
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import imgstore
from utilities import *
import stim_handling as stims



def sync_by_reversal(df, col='dir', X=20000):
    """
    pass a df with stim information
    returns the df with -"timeSinceOnset", showing seconds since stim info changed
                        - rotation values adjusted for direction so rotation of new stim is positive
    """
    df = df.sort_values('FrameNumber')
    df = df[df.index < X]
    df['reversal'] = 0
    reversals = df[abs(df[col] - df.shift()[col]) ==2].index
    df.loc[reversals, 'reversal'] = 1
    df['firstStim'] = 0
    firstStim = df[df['Time'] < df['Time'].median()]
    firstStim = firstStim[abs(firstStim[col] - firstStim.shift()[col]) ==1].index
    df.loc[firstStim, 'firstStim'] = 1
    df['lastStim'] = 0
    lastStim = df[df['Time'] > df['Time'].median()]
    lastStim = lastStim[abs(lastStim[col] - lastStim.shift()[col]) ==1].index
    df.loc[lastStim, 'lastStim'] = 1
    return df

def align_by_stim(df, ID, stimAligner='reversal', col='median_dRotation'):
    df = df[df[col].isnull() == False]
    alignPoints = list(df[df[stimAligner] == 1]['Timestamp'].values)
    trials = pd.DataFrame()
    trialID = 0        
    for i in alignPoints:
        data = df.loc[df['Timestamp'].between(i-10.0, i+60.0), ['Timestamp','dir',col]]
        data.index = pd.to_timedelta(data['Timestamp']-i,'s') 
        data[col] = data[col]*data['dir'].median()*-1.0 #make congruent and positive
        data['trialID'] = ID + '_' + str(trialID)
        trialID += 1
        trials = pd.concat([trials, data], axis=0)
    return trials
        
def plot_many_trials(trials, col='median_dRotation', grouping='trialID', plotMean=True, fig= None, ax=None, colour=None):
  
    if fig== None:
        fig = plt.figure()
        ax = fig.add_subplot(111) 
    if grouping == 'trialID': 
        g = trials.groupby(grouping)
        LW = 0.5
        ALPHA = 0.5
    else:
        trials = trials.resample('200L').mean()
        g = trials.groupby(grouping)
        LW = 2
        ALPHA = 1.0
    for a, data in g:
        ax.plot(data.index, data[col], label=str(a), linewidth=LW, alpha=ALPHA)
    
    if plotMean == True:
        trials = trials.resample('200L').mean()
        g = trials.groupby(trials.index).mean()
        ax.plot(g.index, g[col], label='mean', linewidth=2, color='k')
    
    ax.set_xlabel('Time since reversal (s)')
    ax.set_ylabel('Congruent rotation')
    ax.set_ylim(-1.05, 1.05)
    ax.set_yticks([-1.0, 0, 1.0])
    plt.legend()
    return fig
 
 
 
groupsizes = [64,128,256,512,1024]

allData = pd.DataFrame()
for groupsize in groupsizes:
    print groupsize
    groupData = pd.DataFrame()
    for fn in glob.glob('/media/recnodes/recnode_2mfish/reversals3m_' + str(groupsize) + '_dotbot_*/track/perframe_stats.pickle'):
        print fn
        ret, pf = stims.sync_reversals(pd.read_pickle(fn), stims.get_logfile(fn.rsplit('/',2)[0]), imgstore.new_for_filename(fn.rsplit('/',2)[0] + '/metadata.yaml'))
        pf['dir'] = pd.to_numeric(pf['dir'], errors='coerce')
        pf = sync_by_reversal(pf)
        fileID = fn.split('/')[-3].split('.')[0].split('_',3)[-1]
        reversals = align_by_stim(pf, fileID)
        reversals['groupsize'] = groupsize
        groupData = pd.concat([groupData, reversals], axis=0)
    groupData.to_pickle('/media/recnodes/Dan_storage/190503_reversal_data_compiled_' + str(groupsize) + '.pickle')
    plot_many_trials(groupData)
    plt.savefig('/media/recnodes/Dan_storage/190503_reversal_' + str(groupsize) + '.svg')
    plt.close('all')
    allData = pd.concat([allData, groupData], axis=0)
plot_many_trials(allData, plotMean=False, grouping='groupsize')
plt.savefig('/media/recnodes/Dan_storage/190503_reversal_means.svg')
allData.to_pickle('/media/recnodes/Dan_storage/190503_reversal_data_compiled_full.pickle')
        


    
