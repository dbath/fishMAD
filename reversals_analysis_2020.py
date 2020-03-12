
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import imgstore
from utilities import *
import stim_handling as stims
from scipy.interpolate import splrep, splev


def sync_by_reversal(df, col='dir'):
    """
    pass a df with stim information
    returns the df with rotation values adjusted for direction so rotation of new stim is positive
    """
    df = df.sort_values('Timestamp').reset_index()
    df = df[:-10]
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
    alignPoints = list(df[df[stimAligner] == 1]['Timestamp'].values)
    df = df[df[col].isnull() == False]
    trials = pd.DataFrame()
    trialID = 0        
    for i in alignPoints:
        data = df.loc[df['Timestamp'].between(i-10.0, i+60.0), ['Timestamp','speed','dir','coh',
                                                                'mean_polarization',
                                                                'mean_radius',
                                                                'median_radius',
                                                                'median_swimSpeed',
                                                                'median_dRotation_cArea', 
                                                                'median_dRotation_cMass',
                                                                'std_dRotation_cArea',
                                                                'std_dRotation_cMass',
                                                                'entropy_Ra']]
        data['syncTime'] = pd.to_timedelta(data['Timestamp']-i,'s') 
        data['median_dRotation_cArea'] = data['median_dRotation_cArea']*data['dir'].median()*-1.0 #make congruent and positive
        data['median_dRotation_cMass'] = data['median_dRotation_cMass']*data['dir'].median()*-1.0 #make congruent and positive

        data['trialID'] = ID + '_' + str(trialID)
        data['date'] = ID.split('_')[0]
        trialID += 1
        trials = pd.concat([trials, data], axis=0)
    return trials
        
def getMinMax(series, buffer=0.05):
    MIN = series.min()
    if MIN < 0: 
        MIN*= 1.0 + buffer
    else:
        MIN*=1.0 - buffer
    if series.max() < 0:
        MAX = series.max() *(1.0-buffer)
    else:
        MAX = series.max() *(1.0+buffer)
    return (MIN, MAX)

def plot_many_trials(trials, col='median_dRotation_cArea', grouping='trialID', plotTrials=True, fig= None, ax=None, colour=None, XLIM=(-10,60), YLIM=(-1.05,1.05), RESAMPLE='250ms', NORMALIZE_PRESTIM=False, YLABEL='Mean congruent rotation order $\pm$ SEM'):
    #colourList = ['#EA4335','#E16D13','#FBBC05','#34A853','#4285F4','#891185',
    #              '#4285F4','#FBBC05','#34A853','#EA4335','#891185','#E16D13','#0B1C2E','#347598']

    trials.index = trials.syncTime

    if YLIM == 'auto':
        foo = trials.copy()
        YLIM = getMinMax(foo.resample(RESAMPLE).mean().groupby([grouping,'syncTime']).mean()[col], buffer=0.1)

    if fig== None:
        fig = plt.figure()
        ax = fig.add_subplot(111) 
    if grouping == 'trialID': 
        g = trials.groupby(grouping)
        LW = 0.5
        ALPHA = 0.5
        for a, data in g:
            #data.index = data['syncTime']
            data = data.resample(RESAMPLE).mean()
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
                vals = vals.resample(RESAMPLE).mean()
                xvals = [t.total_seconds() for t in vals.index]
                ax.plot(xvals, vals[col], label=LABEL, 
                                                linewidth=LW, 
                                                alpha=ALPHA, 
                                                color=colourList[groupCount])
                LABEL = '_nolegend_'
            groupCount += 1
    else:
        g = trials.groupby([grouping])
        LW = 0.5
        ALPHA = 0.5
        groupCount = 0
        for group, data in g:
            if grouping == 'coh':
                if not group in [0,0.2,0.4,0.6,0.8,1.0]:
                    continue
            N = len(set(data['trialID']))
            LABEL = str(group) + ', N=' + str(int(N))
            if plotTrials == True:
                h = data.groupby('trialID')
                for a, vals in h:
                    ax.plot(vals.index, vals[col], label=LABEL, 
                                                    linewidth=LW, 
                                                    alpha=ALPHA, 
                                                    color=colourList[groupCount])
                    LABEL = '_nolegend_'
            data.index = data['syncTime']
            r = data.resample(RESAMPLE).mean()
            sem = 1.253*(data.resample(RESAMPLE).std()/np.sqrt(N)) #http://davidmlane.com/hyperstat/A106993.html and
            #    https://influentialpoints.com/Training/standard_error_of_median.htm
            xvals = [i.total_seconds()  for i in r.index]
            prestimIdx = (np.array(xvals) < 0) * (np.array(xvals)>-1)
            if NORMALIZE_PRESTIM:
                a = r.loc[prestimIdx, col].mean() #normalization value for variation in prestim
            else:
                a=0
            ax.plot(xvals, r[col]-a, label=LABEL, linewidth=2, color=colourList[groupCount], zorder=100)
            ax.fill_between(xvals, 
                            r[col]-a+sem[col], 
                            r[col]-a-sem[col], 
                            color=colourList[groupCount], 
                            alpha=0.1, 
                            linewidth=0,
                            zorder=10)
            groupCount+=1

    #fig.autofmt_xdate()
    ax.set_xlabel('Time since direction change (s)')#, fontsize='xx-small')

    
    if NORMALIZE_PRESTIM:
        ax.set_ylabel('Normalized ' + YLABEL)#, fontsize='xx-small')
    else:
        ax.set_ylabel(YLABEL)#, fontsize='xx-small')
    ax.set_ylim(YLIM[0], YLIM[1])
    #ax.set_yticks([-1.0, 0, 1.0])
    ax.set_xlim(XLIM[0], XLIM[1])
    if grouping == 'coh':
        plt.legend(title='Coherence', fontsize='xx-small')
    else:
        plt.legend(title=grouping, fontsize='xx-small')
    #plotnice()
    return fig
    
groupsizes = [64,128,256,512,1024]
"""
allData = pd.DataFrame()

for groupsize in groupsizes:
    print groupsize
    groupData = pd.DataFrame()
    for fn in glob.glob('/media/recnodes/recnode_2mfish/reversals3m_' + str(groupsize) + '_dotbot_*/track/perframe_stats.pickle'):
        if '20181026' in fn:#day when fish were left in the tank overnight
            continue
        if '20190523' in fn:#on this day, timestamps were out of sync by ~25 seconds
            continue
        if '20190603' in fn:#on this day, timestamps were out of sync by ~25 seconds
            continue
        print fn
        try:
            pf = pd.read_pickle(fn)
            if not 'FrameNumber' in pf.columns:
                if not 'frame' in pf.columns:
                    pf['frame'] = pf.index.copy()           
                ret, pf = stims.sync_reversals(pf, stims.get_logfile(fn.rsplit('/',2)[0]), imgstore.new_for_filename(fn.rsplit('/',2)[0] + '/metadata.yaml'))
        except Exception as e:
            print "failed for ", fn
            print e
            continue
        pf['dir'] = pd.to_numeric(pf['dir'], errors='coerce')

        
        pf = sync_by_reversal(pf)
        fileID = fn.split('/')[-3].split('.')[0].split('_',3)[-1]
        reversals = align_by_stim(pf, fileID)
        if len(reversals) == 0:
            continue
        reversals['groupsize'] = groupsize

        groupData = pd.concat([groupData, reversals], axis=0)
    groupData.to_pickle('/media/recnodes/Dan_storage/20200203_reversal_data_compiled_' + str(groupsize) + '.pickle')

    allData = pd.concat([allData, groupData], axis=0)
allData.to_pickle('/media/recnodes/Dan_storage/20200203_reversal_data_compiled_full.pickle')
"""
allData = pd.read_pickle('/media/recnodes/Dan_storage/20200203_reversal_data_compiled_full.pickle')

colourList = create_colourlist(len(groupsizes), cmap='viridis')
for COL in ['median_dRotation_cArea','median_dRotation_cMass']:
    plot_many_trials(allData, col=COL, grouping='groupsize', plotTrials=False)
    plt.savefig('/media/recnodes/Dan_storage/20200312_reversals_'+COL+'_vs_time_by_groupsize.svg')
    plt.close('all')
    plot_many_trials(allData, col=COL, grouping='groupsize', plotTrials=False, XLIM=(-5,15), RESAMPLE='25ms', NORMALIZE_PRESTIM=False)
    plt.savefig('/media/recnodes/Dan_storage/20200312_reversals_'+COL+'_vs_time_by_groupsize_onset.svg')
    plt.close('all')

#colourList = ['#EA4335', '#E16D13', '#FBBC05', '#34A853', '#4285F4', '#891185', '#4285F4', '#FBBC05', '#34A853', '#EA4335', '#891185', '#E16D13', '#0B1C2E','#347598']
cols = ['mean_polarization',
         'mean_radius',
         'median_radius',
         'median_swimSpeed',
         'entropy_Ra',
         'std_dRotation_cArea']


allData['rA_rounded'] = np.around(allData['median_dRotation_cMass']/10.0, 2)*10.0 
rev = allData[allData.syncTime.between(np.timedelta64(-10, 's'), np.timedelta64(30,'s'))]

g = rev.groupby('groupsize')         
#PLOT BY GROUPING BY ROTATION ORDER
ymax, xmax = (4000,6000)
my_dpi = 300
my_figsize = [xmax/my_dpi, ymax/my_dpi]
fig  = plt.figure(figsize=my_figsize, dpi=my_dpi)
p = 0
for col in cols:
    p+=1
    i=1
    for gs, data in g:
        axi = fig.add_subplot(2,3,p)
        data.index=data['syncTime']
        N = len(set(data.trialID))
        foo = data.groupby('rA_rounded')
        m = foo.mean()
        s = foo.std()/np.sqrt(N)
        plt.fill_between(m.median_dRotation_cMass, m[col]+s[col], m[col]-s[col], color=colourList[i-1], alpha=0.1, linewidth=0) 
        plt.plot(m.median_dRotation_cMass, m[col], color=colourList[i-1],label=gs) 
        plt.legend() 
        axi.set_ylabel(col) 
        i+=1
plt.savefig('/media/recnodes/Dan_storage/20200312_reversals_misc_vs_dRotationMass_binsize_0.1.svg')  


#FIRST GROUP BY TIME, THEN PLOT VS ROTATION ORDER

fig  = plt.figure(figsize=my_figsize, dpi=my_dpi)
p = 0
for col in cols:
    p+=1
    i=1
    for gs, data in g:
        axi = fig.add_subplot(2,3,p)
        data.index=data['syncTime']
        N = len(set(data.trialID))
        foo = data.resample('250ms')
        m = foo.mean()
        s = foo.std()/np.sqrt(N)
        plt.fill_between(m.median_dRotation_cMass, m[col]+s[col], m[col]-s[col], color=colourList[i-1], alpha=0.1, linewidth=0) 
        plt.plot(m.median_dRotation_cMass, m[col], color=colourList[i-1],label=gs) 
        plt.legend() 
        axi.set_ylabel(col) 
        i+=1
plt.savefig('/media/recnodes/Dan_storage/20200312_reversals_misc_vs_dRotationMass_250msBins.svg') 


