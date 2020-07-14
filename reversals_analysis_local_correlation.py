import pandas as pd
import numpy as np
import joblib
import stim_handling as stims
from utilities import *
import imgstore

from scipy.stats import spearmanr





def get_trial_data(MAIN_DIR):
    
    try:
        fbf = pd.read_pickle(MAIN_DIR + 'track/frameByFrameData.pickle') 
        assert len(fbf.shape) > 1
    except:
        fbf = joblib.load(MAIN_DIR + 'track/frameByFrameData.pickle') 
        assert len(fbf.shape) > 1
    fbf['trackid'] = fbf['trackid'].astype(int) 
    try:
        l = pd.read_pickle(MAIN_DIR + 'track/localData_FBF.pickle') 
        assert len(l.shape) > 1
    except:
        l = joblib.load(MAIN_DIR + 'track/localData_FBF.pickle') 
        assert len(l.shape) > 1
    l['trackid'] = l['trackid'].astype(int) 
    l['frame'] = l['frame'].astype(int) 


    df = pd.merge(fbf,l,how='left', left_on=['frame','trackid'], right_on=['frame','trackid']) 
    store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml') 
    log = stims.get_logfile(MAIN_DIR) 
    
    ret, synced = stims.sync_data(df, log, store) 
    #calculate individual rotation data:
    synced['CX'] = synced[XPOS] - 160 
    synced['CY'] = synced[YPOS] - 167 
    synced['radius'] = np.sqrt(synced['CX']**2 + synced['CY']**2) 
    synced['uCX'] = synced['CX'] / synced['radius'] 
    synced['uCY'] = synced['CY'] / synced['radius'] 
    synced['uVX'] = synced[XVEL] / synced[SPEED] 
    synced['uVY'] = synced[YVEL] / synced[SPEED] 
    synced['Rotation'] = np.cross(synced[['uCX','uCY']], synced[['uVX','uVY']]) 

    synced = synced.sort_values('Timestamp').reset_index()
    synced = synced[:-10]
    synced['reversal'] = 0
    reversals = synced[abs(synced['dir'] - synced.shift()['dir']) ==2].index
    synced.loc[reversals, 'reversal'] = 1
    synced.loc[synced['Time'] > 300, 'reversal'] = 0 #FIXME this is a hack solution to sort out ends
    synced['firstStim'] = 0
    firstStim = synced[synced['Time'] < synced['Time'].median()]
    firstStim = firstStim[abs(firstStim['dir'] - firstStim.shift()['dir']) ==1].index
    synced.loc[firstStim, 'firstStim'] = 1
    synced['lastStim'] = 0
    lastStim = synced[synced['Time'] > synced['Time'].median()]
    lastStim = lastStim[abs(lastStim['dir'] - lastStim.shift()['dir']) ==1].index
    synced.loc[lastStim, 'lastStim'] = 1

    alignPoints = list(synced[synced['reversal'] == 1]['Timestamp'].values)
    synced = synced[synced['dir'].isnull() == False]
    trials = pd.DataFrame()
    fileID = MAIN_DIR.split('/')[-2].split('.')[0].split('_',3)[-1]
    trialID = 0        
    for i in alignPoints:
        data = synced.loc[synced['Timestamp'].between(i-10.0, i+60.0), ['Timestamp','speed','dir','coh','frame',
                       'neighbourDist', 'localArea', 'localPackingFraction',
                       'localMedianRotation', 'localRscore', 'localPolarization', 
                       'localPDcor','localSpeedScore',
                       'radius', 'Rotation']]
        data['syncTime'] = pd.to_timedelta(data['Timestamp']-i,'s') 
        data['localMedianRotation'] = data['localMedianRotation']*np.sign(data['dir'].median())*-1.0 #make congruent and positive
        data['Rotation'] = data['Rotation']*np.sign(data['dir'].median())*-1.0 #make congruent and positive
        data.index = data['syncTime']
        data['syncTime'] = data.index.copy()
        GBF = data.resample('250ms')
        median = GBF.median()
        
        median['Spearman_Rotation_neighbourDist'] = [spearmanr(x['Rotation'],x['neighbourDist'])[0] for i,x in GBF]
        median['Spearman_Rotation_localArea'] = [spearmanr(x['Rotation'],x['localArea'])[0] for i,x in GBF]
        median['Spearman_Rotation_localPackingFraction'] = [spearmanr(x['Rotation'],x['localPackingFraction'])[0] for i,x in GBF]
        median['Spearman_Rotation_localMedianRotation'] = [spearmanr(x['Rotation'],x['localMedianRotation'])[0] for i,x in GBF]
        median['Spearman_Rotation_localPolarization'] = [spearmanr(x['Rotation'],x['localPolarization'])[0] for i,x in GBF]
        median['Spearman_Rotation_localPDcor'] = [spearmanr(x['Rotation'],x['localPDcor'])[0] for i,x in GBF]
        median['Spearman_Rotation_localSpeedScore'] = [spearmanr(x['Rotation'],x['localSpeedScore'])[0] for i,x in GBF]
        median['Spearman_Rotation_radius'] = [spearmanr(x['Rotation'],x['radius'])[0] for i,x in GBF]

        median['trialID'] = fileID + '_' + str(trialID)
        median['date'] = fileID.split('_')[0]
        trialID += 1
        trials = pd.concat([trials, median], axis=0)

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

def plot_many_trials(trials, col='median_dRotation_cArea', grouping='trialID', plotTrials=True, fig= None, ax=None, colour=None, XLIM=(-10,60), YLIM="auto", RESAMPLE='250ms', NORMALIZE_PRESTIM=False, YLABEL="Auto"):
    #colourList = ['#EA4335','#E16D13','#FBBC05','#34A853','#4285F4','#891185',
    #              '#4285F4','#FBBC05','#34A853','#EA4335','#891185','#E16D13','#0B1C2E','#347598']

    trials.index = trials.syncTime

    #if YLIM == 'auto':
    #    foo = trials.copy()
    #    YLIM = getMinMax(foo.resample(RESAMPLE).mean().groupby([grouping,'syncTime']).mean()[col], buffer=0.1)

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
    
    if YLABEL == "Auto":
        YLABEL = ' '.join(col.split('_')) + "$\pm$ SEM"
    
    if NORMALIZE_PRESTIM:
        ax.set_ylabel('Normalized ' + YLABEL)#, fontsize='xx-small')
    else:
        ax.set_ylabel(YLABEL)#, fontsize='xx-small')
    if not YLIM == "auto":
        ax.set_ylim(YLIM[0], YLIM[1])
    #ax.set_yticks([-1.0, 0, 1.0])
    ax.set_xlim(XLIM[0], XLIM[1])
    if grouping == 'coh':
        plt.legend(title='Coherence', fontsize='xx-small')
    else:
        plt.legend(title=grouping, fontsize='xx-small')
    #plotnice()
    return fig



    

groupsizes = [64,128,256,512]#,1024]

allData = pd.DataFrame()


for groupsize in groupsizes:
    print(groupsize)
    groupData = pd.DataFrame()
    for fn in glob.glob('/media/recnodes/recnode_2mfish/reversals3m_' + str(groupsize) + '_dotbot_*/track/localData_FBF.pickle'):
        #if '20181026' in fn:#day when fish were left in the tank overnight
        #    continue
        if '20190523' in fn:#on this day, timestamps were out of sync by ~25 seconds
            continue
        if '20190603' in fn:#on this day, timestamps were out of sync by ~25 seconds
            continue
        print(fn)
        try:
            data = get_trial_data(fn.split('track/')[0])
            data['groupsize'] = groupsize
        except Exception as e:
            print("failed for ", fn)
            print(e)
            continue
    
        groupData = pd.concat([groupData, data], axis=0, sort=True)
    groupData.to_pickle('/media/recnodes/Dan_storage/20200713_reversal_local_data_compiled_' + str(groupsize) + '.pickle')
    #allData = pd.concat([allData, groupData], axis=0)

1/0
allData.to_pickle('/media/recnodes/Dan_storage/20200713_reversal_local_data_compiled_full.pickle')

allData = pd.read_pickle('/media/recnodes/Dan_storage/20200713_reversal_local_data_compiled_full.pickle')

colourList = create_colourlist(len(groupsizes), cmap='viridis')

COLS = [ 'neighbourDist',
         'localArea',
         'localPackingFraction',
         'localMedianRotation',
         'localRscore',
         'localPolarization',
         'localPDcor',
         'localSpeedScore',
         'radius',
         'Rotation',
         'Spearman_Rotation_neighbourDist',
         'Spearman_Rotation_localArea',
         'Spearman_Rotation_localPackingFraction',
         'Spearman_Rotation_localMedianRotation',
         'Spearman_Rotation_localPolarization',
         'Spearman_Rotation_localPDcor',
         'Spearman_Rotation_localSpeedScore',
         'Spearman_Rotation_radius']





for COL in COLS:
    plot_many_trials(allData, col=COL, grouping='groupsize', plotTrials=False)
    plt.savefig('/media/recnodes/Dan_storage/20200713_reversals_'+COL+'_vs_time_by_groupsize.svg')
    plt.close('all')
    plot_many_trials(allData, col=COL, grouping='groupsize', plotTrials=False, XLIM=(-5,15), RESAMPLE='25ms', NORMALIZE_PRESTIM=False)
    plt.savefig('/media/recnodes/Dan_storage/20200713_reversals_'+COL+'_vs_time_by_groupsize_onset.svg')
    plt.close('all')




#RANK TRIALS WITHIN GROUP SIZES AND GROUP TO COMPARE EFFECTS OF PRE-STIM DENSITY ETC

prestim = allData.loc[allData.syncTime < np.timedelta64(0),:]  

prestim_means = prestim.groupby('trialID').mean()


rankcols = ['Rotation',
            'localArea',
            'localMedianRotation',
            'localPDcor',
            'localPackingFraction', 
            'localPolarization', 
            'localRscore',
            'localSpeedScore', 
            'neighbourDist', 
            'radius'
            ]
            
for group, data in prestim_means.groupby('groupsize'): 
    for col in rankcols: 
        prestim_means.loc[data.index,col + '_rank'] = rank_on_column(data, col, 3) 

ranks = prestim_means.loc[:,prestim_means.columns[-1*len(rankcols):] ] 


foo = allData.merge(ranks, left_on='trialID', right_index=True)

colourList = create_colourlist(3, cmap='viridis')

fig = plt.figure() 
for colnum in range(len(ranks.columns)): 
    ax = fig.add_subplot(2,5,colnum+1) 
    plot_many_trials(foo, grouping=ranks.columns[colnum], plotTrials=False, col='Rotation', fig=fig, ax=ax)  

plt.savefig('/media/recnodes/Dan_storage/20200714_reversals_grouped_by_prestim_rank_local_features.svg')


