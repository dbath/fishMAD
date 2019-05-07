
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import imgstore
from utilities import *
import stim_handling as stims



def sync_by_reversal(df, col='dir', X=20000):
    """
    pass a df with stim information
    returns the df with rotation values adjusted for direction so rotation of new stim is positive
    """
    df = df.sort_values('FrameNumber')
    df = df[df.index < X]
    df['reversal'] = 0
    reversals = df[abs(df[col] - df.shift()[col]) ==2].index
    df.loc[reversals, 'reversal'] = 1
    df.loc[df['Time'] > 300, 'reversal'] = 0 #FIXME this is a hack solution to sort out ends
    df['firstStim'] = 0
    firstStim = df[df['Time'] < df['Time'].median()]
    firstStim = firstStim[abs(firstStim[col] - firstStim.shift()[col]) ==1].index
    df.loc[firstStim, 'firstStim'] = 1
    df['lastStim'] = 0
    lastStim = df[df['Time'] > df['Time'].median()]
    lastStim = lastStim[abs(lastStim[col] - lastStim.shift()[col]) ==1].index
    df.loc[lastStim, 'lastStim'] = 1
    return df

def align_by_stim(df, ID, stimAligner='reversal', col='median_dRotation_cArea'):
    df = df[df[col].isnull() == False]
    alignPoints = list(df[df[stimAligner] == 1]['Timestamp'].values)
    trials = pd.DataFrame()
    trialID = 0        
    for i in alignPoints:
        data = df.loc[df['Timestamp'].between(i-10.0, i+60.0), ['Timestamp','dir',col]]
        data.index = pd.to_timedelta(data['Timestamp']-i,'s') 
        data[col] = data[col]*data['dir'].median()*-1.0 #make congruent and positive
        data['trialID'] = ID + '_' + str(trialID)
        data['date'] = ID.split('_')[0]
        trialID += 1
        trials = pd.concat([trials, data], axis=0)
    return trials
        
def plot_many_trials(trials, col='median_dRotation_cArea', grouping='trialID', plotMean=True, fig= None, ax=None, colour=None):
    colourList = ['#4285F4','#FBBC05','#34A853','#EA4335','#891185','#E16D13','#0B1C2E','#347598']

    if fig== None:
        fig = plt.figure()
        ax = fig.add_subplot(111) 
    if grouping == 'trialID': 
        g = trials.groupby(grouping)
        LW = 0.5
        ALPHA = 0.5
        for a, data in g:
            ax.plot(data.index, data[col], label=str(a), linewidth=LW, alpha=ALPHA)
    elif grouping == 'byday': 
        g = trials.groupby(['date'])
        LW = 0.5
        ALPHA = 0.5
        groupCount = 0
        for date, data in g:
            h = data.groupby('trialID')
            LABEL = date
            for a, vals in h:
                ax.plot(vals.index, vals[col], label=LABEL, 
                                                linewidth=LW, 
                                                alpha=ALPHA, 
                                                color=colourList[groupCount])
                LABEL = '_nolegend_'
            groupCount += 1
    else:
        g = trials.groupby(grouping)
        LW = 2
        ALPHA = 1.0
        for a, data in g:
            data = data.resample('200L').mean()
            ax.plot(data.index, data[col], label=str(a), linewidth=LW, alpha=ALPHA)

    if plotMean == True:
        trials = trials.resample('200L').mean()
        g = trials.groupby(trials.index).mean()
        ax.plot(g.index, g[col], label='mean', linewidth=2, color='k')
    
    fig.autofmt_xdate()
    ax.set_xlabel('Time since reversal (s)')
    ax.set_ylabel('Congruent rotation')
    ax.set_ylim(-1.05, 1.05)
    ax.set_yticks([-1.0, 0, 1.0])
    plt.legend()
    plotnice()
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
    plot_many_trials(groupData, col='median_dRotation_cArea', grouping='byday')
    plt.savefig('/media/recnodes/Dan_storage/190503_reversal_' + str(groupsize) + '.svg')
    plt.close('all')
    allData = pd.concat([allData, groupData], axis=0)
plot_many_trials(allData, plotMean=False, grouping='groupsize')
plt.savefig('/media/recnodes/Dan_storage/190503_reversal_means.svg')
allData.to_pickle('/media/recnodes/Dan_storage/190503_reversal_data_compiled_full.pickle')
        


    
