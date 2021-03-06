
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import imgstore
from utilities import *
import stim_handling as stims

blacklist = [
             '/media/recnodes/kn-crec06/coherencetestangular_16_dotbot_20180409_135500/track/perframe_stats.pickle', #no log file
             '/media/recnodes/kn-crec05/coherencetestangular_64_dotbot_20171219_161400/track/perframe_stats.pickle', #multiple stimuli
             '/media/recnodes/kn-crec05/coherencetestangular_64_dotbot_20171219_163400/track/perframe_stats.pickle', #multiple stimuli
             '/media/recnodes/kn-crec05/coherencetestangular_64_dotbot_20171219_165400/track/perframe_stats.pickle', #multiple stimuli
             '/media/recnodes/kn-crec05/coherencetestangular_64_dotbot_20171219_171401/track/perframe_stats.pickle', #multiple stimuli
             '/media/recnodes/kn-crec05/coherencetestangular_64_dotbot_20171219_173400/track/perframe_stats.pickle', #multiple stimuli
             '/media/recnodes/kn-crec06/coherencetestangular_64_dotbot_20171219_173501/track/perframe_stats.pickle', #multiple stimuli
             '/media/recnodes/kn-crec06/coherencetestangular_64_dotbot_20171219_171502/track/perframe_stats.pickle', #multiple stimuli
             '/media/recnodes/kn-crec06/coherencetestangular_64_dotbot_20171219_165501/track/perframe_stats.pickle', #multiple stimuli
             '/media/recnodes/kn-crec06/coherencetestangular_64_dotbot_20171219_163500/track/perframe_stats.pickle', #multiple stimuli
             '/media/recnodes/kn-crec06/coherencetestangular_64_dotbot_20171219_161501/track/perframe_stats.pickle' #multiple stimuli
             

            ]


def sync_by_stimStart(df, col='speed'):
    """
    pass a df with stim information
    returns the df with rotation values adjusted for direction so rotation of new stim is positive
    """
    df = df.sort_values('FrameNumber').reset_index()
    df = df[:-10] #drop end to avoid dealing with annoying NaN cases #lazy #FIXME
    
    df.loc[:,'stimStart'] = 0
    firstStim = df.loc[df['Time'] < df['Time'].median(), 'speed'].idxmax()
    df.loc[firstStim, 'stimStart'] = 1
    df.loc[:,'stimEnd'] = 0
    lastStim = df.loc[df['Time'] > df['Time'].median(), 'speed'].idxmin()
    df.loc[lastStim, 'stimEnd'] = 1
    return df

def align_by_stim(df, ID, stimAligner='stimStart', col='median_dRotation_cArea'):
    df = df[df[col].isnull() == False]
    alignPoints = list(df[df[stimAligner] == 1]['Timestamp'].values)
    trials = pd.DataFrame()
    trialID = 0        
    i = alignPoints[0]#for i in alignPoints:
    data = df.loc[df['Timestamp'].between(i-30.0, i+400.0), ['Timestamp','speed','dir','coh',
                                                            'median_dRotation_cArea', 
                                                            'median_dRotation_cMass',
                                                            'mean_polarization',
                                                            'std_dRotation_cArea',
                                                            'std_dRotation_cMass',
                                                            'pdfPeak1',
                                                            'pdfPeak1_height',
                                                            'pdfPeak2',
                                                            'pdfPeak2_height']]
    data['syncTime'] = pd.to_timedelta(data['Timestamp']-i,'s') 
    DIRECTION = data.loc[data['syncTime'].between(np.timedelta64(0), np.timedelta64(180,'s')), 'dir'].median()*-1.0
    
    #in dec 2017/jan 2018, i changed the way the stimulus direction was recorded:
    if '201712' in ID.split('_')[0]:
        if data['speed'].max() <= 0:
            DIRECTION *=-1.0
    elif '201804' in ID.split('_')[0]:
        DIRECTION *=-1.0
    elif '201806' in ID.split('_')[0]:
        DIRECTION *=-1.0
        

    data['dir'] = data['dir']*DIRECTION #make congruent and positive
    data['median_dRotation_cArea'] = data['median_dRotation_cArea']*DIRECTION #make congruent and positive
    data['median_dRotation_cMass'] = data['median_dRotation_cMass']*DIRECTION #make congruent and positive
    data['pdfPeak1'] = data['pdfPeak1']*DIRECTION #make congruent and positive
    data['pdfPeak2'] = data['pdfPeak2']*DIRECTION #make congruent and positive
    data['trialID'] = ID + '_' + str(trialID)
    data['date'] = ID.split('_')[0]
    trialID += 1
    trials = pd.concat([trials, data], axis=0)

    return trials
        
def plot_many_trials(trials, col='median_dRotation_cArea', grouping='trialID', plotTrials=True, fig= None, ax=None, colour=None, XLIM=(-30,300), RESAMPLE='6s', NORMALIZE_PRESTIM=False, YLABEL='Mean congruent rotation order $\pm$ SEM'):
    colourList = ['#EA4335','#E16D13','#FBBC05','#34A853','#4285F4','#891185',
                  '#4285F4','#FBBC05','#34A853','#EA4335','#891185','#E16D13','#0B1C2E','#347598']

    if fig== None:
        fig = plt.figure()
        ax = fig.add_subplot(111) 
    if grouping == 'trialID': 
        g = trials.groupby(grouping)
        LW = 0.5
        ALPHA = 0.5
        for a, data in g:
            data.index = data['syncTime']
            ax.plot(data.index, data[col], label=str(a), linewidth=LW, alpha=ALPHA)
    elif grouping == 'byday': 
        g = trials.groupby(['date'])
        LW = 0.5
        ALPHA = 0.5
        groupCount = 0
        for date, data in g:
            h = data.groupby('trialID')
            LABEL = date
            vals.index = vas['syncTime']
            for a, vals in h:
                ax.plot(vals.index, vals[col], label=LABEL, 
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
            std = (data.resample(RESAMPLE).std())
            sem = 1.253*std/np.sqrt(N)#(data.resample(RESAMPLE).sem()) #http://davidmlane.com/hyperstat/A106993.html and
            #    https://influentialpoints.com/Training/standard_error_of_median.htm
            xvals = [i.total_seconds() for i in r.index]
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
                            alpha=0.15, 
                            linewidth=0,
                            zorder=10)
            groupCount+=1

    #fig.autofmt_xdate()
    ax.set_xlabel('Time since stimulus onset (s)')#, fontsize='xx-small')

    
    if NORMALIZE_PRESTIM:
        ax.set_ylabel('Normalized ' + YLABEL)#, fontsize='xx-small')
    else:
        ax.set_ylabel(YLABEL)#, fontsize='xx-small')
    ax.set_ylim(-1.05, 1.05)
    ax.set_yticks([-1.0, 0, 1.0])
    ax.set_xlim(XLIM[0], XLIM[1])
    if grouping == 'coh':
        plt.legend(title='Coherence', fontsize='xx-small')
    else:
        plt.legend(title=grouping, fontsize='xx-small')
    plotnice()
    return fig
 
 
 
groupsizes = [8,16,32,64,128]
coherences = [0,0.2,0.4,0.6,0.8,1]
DIRS = ['kn-crec05','kn-crec06','kn-crec07']
allData = pd.DataFrame()
prestim_meanvals = pd.DataFrame()
meanvals = pd.DataFrame()

for groupsize in groupsizes:
    print groupsize
    groupData = pd.DataFrame()
    for DIR in DIRS:
        for fn in glob.glob('/media/recnodes/' + DIR + '/coherencetestangular_' + str(groupsize) + '_dotbot_*/track/perframe_stats.pickle'):
            try:
                if fn.split('/track/perframe_stats')[0] in blacklist:
                    print "excluding", fn
                    continue
                elif '20171219' in fn:
                    print "excluding", fn
                    continue
                print fn
                ret, pf = stims.synch_coherence_with_rotation(pd.read_pickle(fn), stims.get_logfile(fn.rsplit('/',2)[0]), imgstore.new_for_filename(fn.rsplit('/',2)[0] + '/metadata.yaml'))
                pf['dir'] = pd.to_numeric(pf['dir'], errors='coerce')
                pf['coh'] = pf['coh'].fillna(method='pad').fillna(method='backfill')
                pf['coh'] = min(coherences, key=lambda x:abs(x-pf['coh'].median()))

                pf = sync_by_stimStart(pf)
                fileID = fn.split('/')[-3].split('.')[0].split('_',3)[-1]
                aligned = align_by_stim(pf, fileID)
                aligned['groupsize'] = groupsize
                groupData = pd.concat([groupData, aligned], axis=0)
            except Exception as E:
                print "ERROR", fn, '\n', E
                
    groupData.to_pickle('/media/recnodes/Dan_storage/190611_coherence_data_compiled_' + str(groupsize) + 'smalltanks.pickle')
    plot_many_trials(groupData, col='median_dRotation_cArea', grouping='coh', plotTrials=False)
    plt.savefig('/media/recnodes/Dan_storage/190611_dRotationArea_vs_time_by_coherence_' + str(groupsize) + 'smalltanks.svg')
    plt.close('all')
    plot_many_trials(groupData, col='median_dRotation_cArea', grouping='coh', plotTrials=False, XLIM=(-5,25), RESAMPLE='1s', NORMALIZE_PRESTIM=True)
    plt.savefig('/media/recnodes/Dan_storage/190611_dRotationArea_vs_time_by_coherence_' + str(groupsize) + '_onsetsmalltanks.svg')
        
    
    plot_many_trials(groupData, col='mean_polarization', grouping='coh', plotTrials=False)
    plt.savefig('/media/recnodes/Dan_storage/190611_mean_polarization_vs_time_by_coherence_' + str(groupsize) + 'smalltanks.svg')
    plt.close('all')
    plot_many_trials(groupData, col='mean_polarization', grouping='coh', plotTrials=False, XLIM=(-5,25), RESAMPLE='1s')
    plt.savefig('/media/recnodes/Dan_storage/190611_polarization_vs_time_by_coherence_' + str(groupsize) + 'smalltanks_onset.svg')
    
    plot_many_trials(groupData, col='median_dRotation_cMass', grouping='coh', plotTrials=False)
    plt.savefig('/media/recnodes/Dan_storage/190611_dRotationMass_vs_time_by_coherence_' + str(groupsize) + 'smalltanks.svg')
    plt.close('all')
    plot_many_trials(groupData, col='median_dRotation_cMass', grouping='coh', plotTrials=False, XLIM=(-5,25), RESAMPLE='1s', NORMALIZE_PRESTIM=True)
    plt.savefig('/media/recnodes/Dan_storage/190611_dRotationMass_vs_time_by_coherence_' + str(groupsize) + '_onsetsmalltanks.svg')
    
    plot_many_trials(groupData, col='pdfPeak1', grouping='coh', plotTrials=False, YLABEL='Mean PDF Peak Order')
    plt.savefig('/media/recnodes/Dan_storage/190611_pdfPeak1_vs_time_by_coherence_' + str(groupsize) + 'smalltanks.svg')
    plt.close('all')
    plot_many_trials(groupData, col='pdfPeak1', grouping='coh', plotTrials=False, XLIM=(-5,25), RESAMPLE='1s', NORMALIZE_PRESTIM=True, YLABEL='Mean PDF Peak Order')
    plt.savefig('/media/recnodes/Dan_storage/190611_pdfPeak1_vs_time_by_coherence_' + str(groupsize) + '_onsetsmalltanks.svg')
    plt.close('all')
    


    allData = pd.concat([allData, groupData], axis=0)
#plot_many_trials(allData, plotMean=False, grouping='groupsize')
#plt.savefig('/media/recnodes/Dan_storage/190503_reversal_means.svg')
allData.to_pickle('/media/recnodes/Dan_storage/190611_coherence_data_compiled_full_smalltanks.pickle')


for coherence in coherences:
    data = allData.loc[allData['coh']==coherence, :]
    plot_many_trials(data, col='median_dRotation_cArea', grouping='groupsize', plotTrials=False)
    plt.savefig('/media/recnodes/Dan_storage/190611_dRotationArea_vs_time_by_groupsize_'+str(coherence)+'smalltanks.svg')
    plt.close('all')
    plot_many_trials(data, col='median_dRotation_cArea', grouping='groupsize', plotTrials=False, XLIM=(-5,25), RESAMPLE='1s', NORMALIZE_PRESTIM=False)
    plt.savefig('/media/recnodes/Dan_storage/190611_dRotationArea_vs_time_by_groupsize_'+str(coherence)+'_onset.svg')
    plt.close('all')
    plot_many_trials(data, col='median_dRotation_cMass', grouping='groupsize', plotTrials=False)
    plt.savefig('/media/recnodes/Dan_storage/190611_dRotationMass_vs_time_by_groupsize_'+str(coherence)+'smalltanks.svg')
    plt.close('all')
    plot_many_trials(data, col='median_dRotation_cMass', grouping='groupsize', plotTrials=False, XLIM=(-5,25), RESAMPLE='1s', NORMALIZE_PRESTIM=False)
    plt.savefig('/media/recnodes/Dan_storage/190611_dRotationMass_vs_time_by_groupsize_'+str(coherence)+'_onset.svg')
    plt.close('all')
    plot_many_trials(data, col='pdfPeak1',grouping='groupsize', plotTrials=False,YLABEL='Mean PDF Peak Order')
    plt.savefig('/media/recnodes/Dan_storage/190611_pdfPeak1_vs_time_by_groupsize_'+str(coherence)+'smalltanks.svg')
    plt.close('all')
    plot_many_trials(data, col='pdfPeak1',grouping='groupsize', plotTrials=False, XLIM=(-5,25), RESAMPLE='1s', NORMALIZE_PRESTIM=False, YLABEL='Mean PDF Peak Order')
    plt.savefig('/media/recnodes/Dan_storage/190611_pdfPeak1_vs_time_by_groupsize_'+str(coherence)+'_onset.svg')
    plt.close('all')

#allData = pd.read_pickle('/media/recnodes/Dan_storage/190611_coherence_data_compiled_full.pickle')
plot_many_trials(allData, col='median_dRotation_cArea', grouping='coh', plotTrials=False)
plt.savefig('/media/recnodes/Dan_storage/190611_dRotationArea_vs_time_by_coherence_pooled.svg')
plt.close('all')
plot_many_trials(allData, col='median_dRotation_cArea', grouping='coh', plotTrials=False, XLIM=(-5,25), RESAMPLE='1s', NORMALIZE_PRESTIM=False)
plt.savefig('/media/recnodes/Dan_storage/190611_dRotationArea_vs_time_by_coherence_pooled_onset.svg')
plt.close('all')
plot_many_trials(allData, col='median_dRotation_cArea', grouping='coh', plotTrials=False, XLIM=(-5,25), RESAMPLE='1s', NORMALIZE_PRESTIM=True)
plt.savefig('/media/recnodes/Dan_storage/190611_dRotationArea_vs_time_by_coherence_pooled_onset_normed.svg')
plt.close('all')


plot_many_trials(allData, col='median_dRotation_cMass', grouping='coh', plotTrials=False)
plt.savefig('/media/recnodes/Dan_storage/190611_dRotationMass_vs_time_by_coherence_pooled.svg')
plt.close('all')
plot_many_trials(allData, col='median_dRotation_cMass', grouping='coh', plotTrials=False, XLIM=(-5,25), RESAMPLE='1s', NORMALIZE_PRESTIM=False)
plt.savefig('/media/recnodes/Dan_storage/190611_dRotationMass_vs_time_by_coherence_pooled_onset.svg')
plt.close('all')
plot_many_trials(allData, col='median_dRotation_cMass', grouping='coh', plotTrials=False, XLIM=(-5,25), RESAMPLE='1s', NORMALIZE_PRESTIM=True)
plt.savefig('/media/recnodes/Dan_storage/190611_dRotationMass_vs_time_by_coherence_pooled_onset_normed.svg')
plt.close('all')

plot_many_trials(allData, col='pdfPeak1', grouping='coh', plotTrials=False, YLABEL='Mean PDF Peak of Order')
plt.savefig('/media/recnodes/Dan_storage/190611_pdfPeak1_vs_time_by_coherence_pooled.svg')
plt.close('all')
plot_many_trials(allData, col='pdfPeak1', grouping='coh', plotTrials=False, XLIM=(-5,25), RESAMPLE='1s', NORMALIZE_PRESTIM=False, YLABEL='Mean PDF Peak of Order')
plt.savefig('/media/recnodes/Dan_storage/190611_pdfPeak1_vs_time_by_coherence_pooled_onset.svg')
plt.close('all')
plot_many_trials(allData, col='pdfPeak1', grouping='coh', plotTrials=False, XLIM=(-5,25), RESAMPLE='1s', NORMALIZE_PRESTIM=True, YLABEL='Mean PDF Peak of Order')
plt.savefig('/media/recnodes/Dan_storage/190611_pdfPeak1_vs_time_by_coherence_pooled_onset_normed.svg')
plt.close('all')


plot_many_trials(allData, col='mean_polarization', grouping='coh', plotTrials=False)
plt.savefig('/media/recnodes/Dan_storage/190611_polarization_vs_time_by_coherence_pooled.svg')
plt.close('all')
plot_many_trials(allData, col='mean_polarization', grouping='coh', plotTrials=False, XLIM=(-5,25), RESAMPLE='1s', NORMALIZE_PRESTIM=False)
plt.savefig('/media/recnodes/Dan_storage/190611_polarization_vs_time_by_coherence_pooled_onset.svg')
plt.close('all')
    
