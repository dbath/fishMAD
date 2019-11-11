
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from utilities import plotnice
from matplotlib.gridspec import GridSpec
import scipy.stats
import scipy.signal
import glob
import stim_handling as stims
import imgstore
from scipy.interpolate import splrep, splev 

colourlist = ['#EA4335','#E16D13','#FBBC05','#34A853','#4285F4','#891185',
                  '#4285F4','#FBBC05','#34A853','#EA4335','#891185','#E16D13','#0B1C2E','#347598']

coherences = [0,0.2,0.4,0.6,0.8,1]

_bins = [0,1,2,3,4,5,10,15,20,25,30,60,90,120,150,180,240,300,360,420]

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
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_64_dotbot_20190529_115201.stit_WRONG_ched', #WRONG
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_1024_dotbot_20190524_145201.stitched',
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_64_dotbot_20190529_151201.stitched',
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_64_dotbot_20190529_145201.stitched',
             '/media/recnodes/recnode_2mfish/coherencetestangular3m_128_dotbot_20181106_141201.stitched'

            ]

def getOnlyReversals(df, _THRESHOLD=-0.1):
    """
    discard trials where the prestim rotation is positive
    """
    g = df.groupby('trialID')
    newdf = pd.DataFrame()
    for ID, h in g:
        pre = h.loc[h['syncTime'] < np.timedelta64(0), :]
        pre = pre.loc[pre['syncTime'] > np.timedelta64(-10,'s')]
        if pre['smoothedOrotation'].mean() > _THRESHOLD: #remove trials where response is ambiguous
            continue
        h['trialID'] = ID
        newdf = pd.concat([newdf, h], axis=0)
    return newdf
 


def sync_by_RT(df):
    g = df.groupby('trialID')
    newdf = pd.DataFrame()
    for ID, h in g:
        if h['correct'].sum() == 0:
            continue
        pre = h.loc[h['syncTime'] < np.timedelta64(0), :]
        if pre['smoothedOrotation'].mean() > 0: #remove trials where response is ambiguous
            continue

        h['sync_by_RT'] = h['syncTime'] - h.loc[h[h['syncTime'] > np.timedelta64(0)]['correct'].idxmax(), 'syncTime']
        post = h.loc[h['syncTime'] > np.timedelta64(0)]
        newdf = pd.concat([newdf, post], axis=0)
    return newdf
    
def get_bouts(df, col='correct'):
    ons = df.loc[df[col] - df.shift()[col] == 1, 'syncTime'].reset_index(drop=True)
    offs = df.loc[df[col] - df.shift()[col] == -1, 'syncTime'].reset_index(drop=True)
    #if len(ons)== 0 and len(offs) ==0: #if both are none
    #    return pd.DataFrame()
    if len(ons)==0:
        return pd.DataFrame(np.nan, index=[0], columns=['onTime','offTime','duration','IBI','firstBout'], dtype=float)
    elif len(offs)==0:
        offs = pd.Series(df.iloc[-1]['syncTime'])
    
    if len(ons) != len(offs):
        if ons[0] < offs[0]: 
            offs = offs.append(pd.Series(df.iloc[-1]['syncTime']), ignore_index=True)
        elif ons[0] > offs[0]:
            offs = offs.drop(0).reset_index(drop=True)
    else:
        if ons[0] > offs[0]: 
            offs = offs.append(pd.Series(df.iloc[-1]['syncTime']), ignore_index=True)
            offs = offs.drop(0).reset_index(drop=True)
    bouts = pd.DataFrame({'onTime':ons, 'offTime':offs, 'duration':offs-ons})
    bouts['IBI'] = bouts['onTime'] - bouts.shift()['offTime']
    bouts['firstBout'] = bouts['IBI'].isnull()
    bouts['IBI'].fillna(0, inplace=True)
    for col in ['IBI','duration','offTime','onTime']:
        bouts[col] = bouts[col].values.astype(np.float64)/1000000000.0
    return bouts

def get_tau(df, col='correct'):
    """
    pass time series data of post-stimulus only, only if t0 (at stim end) is positive for col
    returns time required for col to drop
    """
    
    return

    
def plot_reaction_times(gd, _bins=_bins, col='correct', PRE_THRESH=0, title='correct responses', XLIM=(0,60)):

    fig = plt.figure(figsize=(8,12))
    count = 0
    gs = GridSpec(3,2, figure=fig)

    peaklist = []
    peakheightlist = []
    bouts = pd.DataFrame()

    for coherence in coherences:
        c = gd.loc[gd['coh'] == coherence, :]
        g = c.groupby('trialID')
        trials = []
        RT = []
        
        ax1 = fig.add_subplot(gs[0,:]) 
        ax2 = fig.add_subplot(gs[1,0])
        ax3 = fig.add_subplot(gs[1,1])
        ax4 = fig.add_subplot(gs[2,0])
        ax5 = fig.add_subplot(gs[2,1])
        for trial, data in g:
            pre = data.loc[data['syncTime'] < np.timedelta64(0)]
            pre = pre.loc[pre['syncTime'] > np.timedelta64(-20, 's')]
            if pre['smoothedOrotation'].mean() > PRE_THRESH: #remove trials where response is ambiguous
                continue

            post = data.loc[data['syncTime'] > np.timedelta64(0)]
            RT.append(post.loc[post[col].idxmax(), 'syncTime'].total_seconds())
            bout = get_bouts(data)
            bout['trialID'] = trial
            bout['coherence'] = coherence
            bouts = pd.concat([bouts, bout],axis=0)

        if len(RT) > 1:
            PDF = scipy.stats.gaussian_kde(RT).pdf(_bins)
            peaks, peakParams = scipy.signal.find_peaks(PDF, 0)
            if len(peaks) >0:
                peaklist.append(_bins[peaks[0]])
                peakheightlist.append(peakParams['peak_heights'][0])
            else:
                peaklist.append(np.nan)
                peakheightlist.append(np.nan)
            ax1.plot(_bins, PDF, label=coherence, color=colourlist[count])
        else:
            peaklist.append(np.nan)
            peakheightlist.append(np.nan)
            
        count +=1
            
        
    ax1.set_xlabel('response time (s)')
    ax1.set_xlim(XLIM)
    plt.legend()
    plotnice('hist', ax=ax1)

    ax2.scatter(coherences, peaklist, c=colourlist[0:len(peaklist)])
    ax2.set_xlabel('coherence')
    ax2.set_ylabel('PDF peak reaction time (s)')
    ax2.set_ylim(0, 1.2*max(peaklist))
    plotnice(ax=ax2)

    ax3.scatter(coherences, peakheightlist, c=colourlist[0:len(coherences)])
    ax3.set_xlabel('coherence')
    ax3.set_ylabel('PDF peak height')
    plotnice(ax=ax3)
    

    _stats = bouts.groupby('coherence').describe()
    
    ax4.bar(coherences,[x.total_seconds() for x in _stats['duration']['mean'].values], color=colourlist[0:len(coherences)], width=0.8/len(coherences)) 
    ax4.errorbar(coherences, [x.total_seconds() for x in _stats['duration']['mean'].values], yerr=[x.total_seconds() for x in _stats['duration']['std'].values], capsize=4, linestyle='None')
    ax4.set_xlabel('coherence')
    ax4.set_ylabel('mean bout duration')
    plotnice(ax=ax4)


    
    ax5.bar(coherences,[x.total_seconds() for x in _stats['IBI']['mean'].values], color=colourlist[0:len(coherences)], width=0.8/len(coherences)) 
    ax5.errorbar(coherences, [x.total_seconds() for x in _stats['IBI']['mean'].values], yerr=[x.total_seconds() for x in _stats['IBI']['std'].values], capsize=4, linestyle='None')
    ax5.set_xlabel('coherence')
    ax5.set_ylabel('mean inter-bout interval')
    plotnice(ax=ax5)
    
    fig.suptitle(title)


    plt.show()
    return RT, bouts.reset_index(drop=True)
    
def set_threshold(gd, THRESHOLD):
    gd.loc[gd['smoothedOrotation'] <= -1.0*THRESHOLD, 'incorrect'] = 1
    gd.loc[gd['smoothedOrotation'] > -1.0*THRESHOLD, 'incorrect'] = 0
    gd.loc[gd['smoothedOrotation'] > THRESHOLD, 'correct'] = 1
    gd.loc[gd['smoothedOrotation'] <= THRESHOLD, 'correct'] = 0
    gd['responding'] = gd['correct'] + gd['incorrect']
    gd.loc[gd['responding'] > 0, 'responding'] = 1 
    return gd

        
def plot_by_RT(trials, col='Orotation', grouping='trialID', plotTrials=True, fig= None, ax=None, colour=None, XLIM=(-30,60), RESAMPLE='1s', NORMALIZE_PRESTIM=False, YLABEL='Mean congruent rotation order $\pm$ SEM'):
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
            data.index = data['sync_by_RT']
            ax.plot(data.index, data[col], label=str(a), linewidth=LW, alpha=ALPHA)
    elif grouping == 'byday': 
        g = trials.groupby(['date'])
        LW = 0.5
        ALPHA = 0.5
        groupCount = 0
        for date, data in g:
            h = data.groupby('trialID')
            LABEL = date
            vals.index = vals['sync_by_RT']
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
            data.index = data['sync_by_RT']
            count = data.resample(RESAMPLE).count()
            removeLowDataCount = count[col] <= 0.2*count[col].max()
            r = data.resample(RESAMPLE).mean()
            sem = 1.253*(data.resample(RESAMPLE).sem()) #http://davidmlane.com/hyperstat/A106993.html and
            #    https://influentialpoints.com/Training/standard_error_of_median.htm
            r[removeLowDataCount] = np.nan
            sem[removeLowDataCount] = np.nan
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
                            alpha=0.05, 
                            linewidth=0,
                            zorder=10)
            groupCount+=1

    #fig.autofmt_xdate()
    ax.set_xlabel('Time since correct response (s)')#, fontsize='xx-small')

    
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
 


def align_by_stim(df, ID, stimAligner='stimStart', col='median_dRotation_cArea'):
    df = df[df[col].isnull() == False]
    alignPoints = list(df[df[stimAligner] == 1]['Timestamp'].values)
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
                                                            'pdfPeak2_height']]
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

def plotnice(plotType='standard', ax=plt.gca()):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if plotType == 'hist':
        ax.spines['left'].set_visible(False)
        ax.set_yticks([])
    elif plotType=='img':
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        plt.axis('off')
    return


"""

        
groupData = pd.DataFrame()
for fn in glob.glob('/media/recnodes/recnode_2mfish/coherencetestangular3m_*_dotbot_*/track/perframe_stats.pickle'):
    expID, groupsize, _, trialID = fn.split('/')[4].split('.')[0].split('_',3)
    if fn.split('/track/perframe_stats')[0] in blacklist:
        print "excluding", fn
        continue
    elif (len(groupData) > 0) and (trialID in set(groupData.trialID)):
        continue
    print fn
    ret, pf = stims.sync_data(pd.read_pickle(fn), stims.get_logfile(fn.rsplit('/',2)[0]), imgstore.new_for_filename(fn.rsplit('/',2)[0] + '/metadata.yaml'))
    pf['dir'] = pd.to_numeric(pf['dir'], errors='coerce')
    pf['coh'] = pf['coh'].fillna(method='pad').fillna(method='backfill')
    #try:
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
    groupData = pd.concat([groupData,newdf], axis=0)
    #except:
    #    print "FAILED"
    #    pass

groupData.to_pickle('/media/recnodes/Dan_storage/190830_reaction_time_precursor.pickle')





"""


THRESHOLDS = [0.8,0.85,0.9,0.95]
minDurs = [0.1,0.3,0.5,0.7] 
groupData = pd.read_pickle('/media/recnodes/Dan_storage/190830_reaction_time_precursor.pickle')

for THRESHOLD in THRESHOLDS:
    for minDur in minDurs:
        groupData.coh = np.around(groupData.coh, 1)

        groupData = set_threshold(groupData, THRESHOLD)

        groupData = getOnlyReversals(groupData, 1.0) #discard trials where prestim >threshold (default -0.1)

        g = groupData.groupby('trialID')

        print "\n\n______________THRESHOLD: ", str(THRESHOLD), "______________\n"
        _RT = []
        bouts = pd.DataFrame()
        trialCount = 0
        correctCount = 0
        for trial, data in g:
            trialCount +=1
            stim_period = data.loc[data['syncTime'] > np.timedelta64(0)]
            stim_period = stim_period.loc[stim_period['syncTime'] < np.timedelta64(300, 's')] #FIXME hardcoded stim duration
            _RT.append(stim_period.loc[stim_period['correct'].idxmax(), 'syncTime'].total_seconds())
            post_stim = data.loc[data['syncTime'] > np.timedelta64(300,'s')] #FIXME hardcoded time

            bout = get_bouts(stim_period)
            md = data.iloc[0] #metadata
            bout['trialID'] = md.trialID
            bout['coh'] = md.coh
            bout['groupsize'] = md.groupsize
            try:
                if stim_period['correct'].mean() > minDur: #FIXME so much thresholding
                    bout['correctTrial'] = 1.0
                    bout['RT'] = stim_period.loc[stim_period['correct'].idxmax(), 'syncTime'].total_seconds()
                    bout['DecayTime'] = post_stim.loc[post_stim['correct'].idxmin(), 'syncTime'].total_seconds()
                else:
                    bout['correctTrial'] = 0.0
                    bout['RT'] = np.nan
                    bout['DecayTime'] = np.nan
                bouts = pd.concat([bouts, bout], axis=0)
            except:
                print "FAILED AT RT AND DECAY TIME", md.trialID
        bouts = bouts.loc[(10.0*bouts['coh'])%2 ==0, :]
        bouts['groupsize'] = bouts['groupsize'].astype(int)
        bouts['coh'] = bouts['coh'].astype(np.float64)

            
        bouts.to_pickle('/media/recnodes/Dan_storage/191023_bouts_t'+ str(minDur) + '_C' + str(THRESHOLD)+ '.pickle')

        n = bouts.groupby('trialID').mean()
        n['coh'] = np.around(n['coh'], 1)
        g = n.groupby(['groupsize','coh'])
        print "COUNTS:\n", g.count()['correctTrial'].unstack()
        print "MEAN:\n", g.mean()['correctTrial'].unstack()
        plt.close('all')
        g['correctTrial'].mean().unstack().plot(kind='line')
        plt.ylabel('Proportion correct trials')
        plt.title('Threshold: '+ str(THRESHOLD)) 
        plt.xlabel('Stimulus coherence')
        plotnice()
        plt.savefig('/media/recnodes/Dan_storage/190902_proportion_correct_trials_vs_groupsize_t'+ str(minDur) + '_C' + str(THRESHOLD) + '.svg')
        
        for col in ['IBI','duration', 'RT']:
            plt.close('all')
            g[col].mean().unstack().plot(kind='line', yerr=g[col].sem().unstack())
            plt.ylabel('Mean ' + col + '(s) $\pm$ SEM')
            plt.title('Threshold: '+ str(THRESHOLD)) 
            plt.xlabel('Stimulus coherence')
            plotnice()
            plt.savefig('/media/recnodes/Dan_storage/190902_' + col + '_vs_groupsize_t'+ str(minDur) + '_C' + str(THRESHOLD) + '.svg')
            
            #n.boxplot(by=['coh','groupsize'], column='correctTrial', rot=90)

