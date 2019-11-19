

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import imgstore
from utilities import *
import stim_handling as stims

blacklist = [
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_64_dotbot_20181023_131202.stitched', #fuzzy. bad tracking?
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_64_dotbot_20181113_165201.stitched', #no stimulus
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_128_dotbot_20181004_161201.stitched', #no stimulus
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_128_dotbot_20181004_163201.stitched', #no stimulus
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_128_dotbot_20181009_133201.stitched', #no stimulus
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_256_dotbot_20181011_101202.stitched', #fuzzy. bad tracking?
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_256_dotbot_20181204_113201.stitched', #no stimulus
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_256_dotbot_20181214_135201.stitched', #truncated file
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_1024_dotbot_20181025_103201.stitched', #fuzzy. bad tracking?
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_1024_dotbot_20190201_105202.stitched', #truncated file.
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_64_dotbot_20190529_115201.stit_WRONG_ched' #WRONG
             

            ]
def plot_many_trials(trials, col='median_dRotation_cArea', grouping='trialID', plotTrials=True, fig= None, ax=None, colour=None, XLIM=(-10,60), YLIM=(-1.05,1.05), RESAMPLE='250ms', NORMALIZE_PRESTIM=False, YLABEL='Mean congruent rotation order $\pm$ SEM'):
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
            for a, vals in h:
                ax.plot(vals['syncTime'], vals[col], label=LABEL, 
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
            sem = 1.253*(data.resample(RESAMPLE).sem()) #http://davidmlane.com/hyperstat/A106993.html and
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
                            alpha=0.05, 
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

from scipy.interpolate import splrep, splev

def align_by_stim(df, ID, stimAligner='stimStart', col='median_dRotation_cArea'):
    alignPoints = list(df[df[stimAligner] == 1]['Timestamp'].values)
    df = df[df[col].isnull() == False]
    trials = pd.DataFrame()
    trialID = 0        
    i = alignPoints[0]#for i in alignPoints:
    data = df.loc[df['Timestamp'].between(i-30.0, i+400.0), ['Timestamp','speed','dir','coh',
                                                            'median_dRotation_cArea', 
                                                            'median_dRotation_cMass',
                                                            'std_dRotation_cArea',
                                                            'std_dRotation_cMass',
                                                            'pdfPeak1',
                                                            'pdfPeak1_height',
                                                            'pdfPeak2',
                                                            'pdfPeak2_height',
                                                            'entropy_Ra']]
    data['syncTime'] = pd.to_timedelta(data['Timestamp']-i,'s') 
    data['median_dRotation_cArea'] = data['median_dRotation_cArea']*data['dir'].median() #make congruent and positive
    data['median_dRotation_cMass'] = data['median_dRotation_cMass']*data['dir'].median() #make congruent and positive
    data['pdfPeak1'] = data['pdfPeak1']*data['dir'].median() #make congruent and positive
    data['pdfPeak2'] = data['pdfPeak2']*data['dir'].median() #make congruent and positive
    data['trialID'] = ID + '_' + str(trialID)
    data['date'] = ID.split('_')[0]
    trialID += 1
    trials = pd.concat([trials, data], axis=0)

    return trials
        
def sync_by_stimStart(df, col='speed'):
    """
    pass a df with stim information
    returns the df with rotation values adjusted for direction so rotation of new stim is positive
    """
    df = df.sort_values('Time')
    df.reset_index(inplace=True)
    df = df[:-10] #drop end to avoid dealing with annoying NaN cases #lazy #FIXME
    
    df.loc[:,'stimStart'] = 0
    firstStim = df.loc[df['Time'] < df['Time'].median(), 'speed'].idxmax()
    df.loc[firstStim, 'stimStart'] = 1
    df.loc[:,'stimEnd'] = 0
    lastStim = df.loc[df['Time'] > df['Time'].median(), 'speed'].idxmin()
    df.loc[lastStim, 'stimEnd'] = 1
    return df

allData = pd.DataFrame()
for fn in glob.glob('/media/recnodes/recnode_2mfish/coherencetestangular3m_*_dotbot_*/track/perframe_stats.pickle'):
    expID, groupsize, _, trialID = fn.split('/')[4].split('.')[0].split('_',3)
    if fn.split('/track/perframe_stats')[0] in blacklist:
        print "excluding", fn
        continue
    print fn
    ret, pf = stims.sync_data(pd.read_pickle(fn), stims.get_logfile(fn.rsplit('/',2)[0]), imgstore.new_for_filename(fn.rsplit('/',2)[0] + '/metadata.yaml'))
    pf['dir'] = pd.to_numeric(pf['dir'], errors='coerce')
    pf['coh'] = pf['coh'].fillna(method='pad').fillna(method='backfill')
    try:
	pf = sync_by_stimStart(pf)
	pf = align_by_stim(pf, trialID)


	#slope = pd.Series(np.gradient(pf['median_dRotation_cArea'].values), pf['Timestamp'], name='slope')
	s = splrep(pf.Timestamp, pf.median_dRotation_cArea, k=5, s=17)
	newdf = pd.DataFrame({'syncTime':pf['syncTime'],
	                      'Orotation':pf['median_dRotation_cArea'], 
	                      'smoothedOrotation':splev(pf.Timestamp, s), 
	                      'dO_by_dt':splev(pf.Timestamp, s, der=1), 
	                      'dO_by_dt2':splev(pf.Timestamp, s, der=2)})
	newdf['groupsize'] = groupsize
	newdf['coh'] = pf['coh'].dropna().mean()
	newdf['trialID'] = trialID
	allData = pd.concat([allData,newdf], axis=0)
    except Exception as e:
        import sys, traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
        #print traceback.print_exception()
        print e
        pass
    
allData.to_pickle('/media/recnodes/Dan_storage/191119_groupdata_coherence_analysis_2.pickle')

prestim = groupData.loc[groupData['syncTime'] < np.timedelta64(0), :]
g = prestim.groupby(['trialID']) 
m = g['Orotation'].median()   
revlist = list(m[m < -0.5].index)
revData = groupData[groupData['trialID'].isin(revlist)]

#normalize entropy data by dividing by ln(groupsize)
allData['entropy_normed'] = allData['entropy_Ra']/np.log(allData['groupsize']) 
#subtract pre-stim baseline entropy
baseline = allData.loc[allData['syncTime'] < np.timedelta64(0), :]
g = baseline.groupby('trialID')  
bases = dict(g['entropy_normed'].mean())
allData['entropy_normed_base'] = allData.loc[:, 'entropy_normed'] - [bases[i] for i in allData['trialID']]

plot_many_trials(allData, col='entropy_Ra', grouping='groupsize', plotTrials=False,
                 YLABEL='Entropy of rotation', YLIM=(1.95,4.05))
                 
plt.savefig('/media/recnodes/Dan_storage/191118_reversals_entropy_vs_time_by_groupsize.svg')
plt.close('all')
plot_many_trials(allData, col='entropy_normed', grouping='groupsize', plotTrials=False, NORMALIZE_PRESTIM=False,YLABEL='Entropy of rotation /ln(N)', YLIM=(0.26,0.82))
plt.savefig('/media/recnodes/Dan_storage/191118_reversals_entropy_lnN_vs_time_by_groupsize.svg')
plt.close('all')
plot_many_trials(allData, col='entropy_normed_base', grouping='groupsize', plotTrials=False, NORMALIZE_PRESTIM=True,YLABEL='Entropy of rotation /ln(N)', YLIM=(-0.06,0.36))
plt.savefig('/media/recnodes/Dan_storage/191118_reversals_normed_entropy_lnN_vs_time_by_groupsize.svg')
plt.close('all')


