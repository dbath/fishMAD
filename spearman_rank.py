
from scipy.stats import spearmanr



def plot_many_spearman(trials, col='median_dRotation_cArea', rankcol='rank_prestim', grouping='trialID', plotTrials=True, fig= None, ax=None, colour=None, XLIM=(-30,400), YLIM=(0,1),RESAMPLE='1s', NORMALIZE_PRESTIM=False, YLABEL='Mean congruent rotation order $\pm$ SEM'):
    colourList = ['#EA4335','#E16D13','#FBBC05','#34A853','#4285F4','#891185',
                  '#4285F4','#FBBC05','#34A853','#EA4335','#891185','#E16D13','#0B1C2E','#347598']

    if fig== None:
        fig = plt.figure()
        ax = fig.add_subplot(111) 

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
        
        data.index = data['syncTime']
        ranksdf = pd.DataFrame()
        for rank, rankdf in data.groupby(rankcol):
            trialsdf = pd.DataFrame()
            for trial, trialdf in rankdf.groupby('trialID'):
                df = trialdf.resample(RESAMPLE).mean()
                trialsdf = pd.concat([trialsdf, trialdf.resample(RESAMPLE).mean()])
            ranksdf = pd.concat([ranksdf, trialsdf.resample(RESAMPLE).mean()])
        
        spear = [spearmanr(x[rankcol],x[col])[0] for i,x in ranksdf.groupby(ranksdf.index.floor(RESAMPLE))]
        pvals = [spearmanr(x[rankcol],x[col])[1] for i,x in ranksdf.groupby(ranksdf.index.floor(RESAMPLE))]
        xvals = [i.total_seconds() for i in ranksdf.resample(RESAMPLE).mean().index]
        prestimIdx = (np.array(xvals) < 0) * (np.array(xvals)>-1)

        ax.plot(xvals, spear, label=LABEL, linewidth=2, color=colourList[groupCount], zorder=100)

        groupCount+=1

    #fig.autofmt_xdate()
    ax.set_xlabel('Time since stimulus onset (s)')#, fontsize='xx-small')
    ax.set_ylabel(YLABEL)#, fontsize='xx-small')
    ax.set_ylim(YLIM[0],YLIM[1])
    #ax.set_yticks([-1.0, 0, 1.0])
    ax.set_xlim(XLIM[0], XLIM[1])
    if grouping == 'coh':
        plt.legend(title='Coherence', fontsize='xx-small')
    elif grouping == 'trialID':
        pass
    else:
        plt.legend(title=grouping, fontsize='xx-small')
    plotnice()
    return fig


def plot_many_spearman_pertrial(trials, col='median_dRotation_cArea', rankcol='rank_prestim', grouping='trialID', plotTrials=True, fig= None, ax=None, colour=None, XLIM=(-30,400), YLIM=(-0.25,1),RESAMPLE='1s', NORMALIZE_PRESTIM=False, YLABEL='Spearman rank correlation',pvalues=False, pvalboundary=0.005, corvals=True):
    colourList = ['#EA4335','#E16D13','#FBBC05','#34A853','#4285F4','#891185',
                  '#4285F4','#FBBC05','#34A853','#EA4335','#891185','#E16D13','#0B1C2E','#347598']

    if fig== None:
        fig = plt.figure()
        ax = fig.add_subplot(111) 

    ax2 = ax.twinx()
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
        
        data.index = data['syncTime']
        trialsdf = pd.DataFrame()
        for trial, trialdf in data.groupby('trialID'):
            df = trialdf.resample(RESAMPLE).mean()
            df['trialID'] = trial
            trialsdf = pd.concat([trialsdf, df])
        ms = trialsdf.loc[trialsdf.index < np.timedelta64(0),:].groupby('trialID').mean()
        ms['ranked_trials'] = rank_on_column(ms, col, len(set(trialsdf.trialID)))
        trialsdf = trialsdf.reset_index().merge(ms.reset_index()[['ranked_trials','trialID']],left_on='trialID',right_on='trialID')
        trialsdf.index = trialsdf['syncTime']
        xvals = [i.total_seconds() for i in trialsdf.resample(RESAMPLE).mean().index]
        if pvalues == True:
            yvals = [spearmanr(x[rankcol],x[col])[1] for i,x in trialsdf.groupby(trialsdf.index.floor(RESAMPLE))]
            ax2.fill_between(xvals, groupCount, groupCount+1, where=np.array(yvals)<pvalboundary, label=LABEL, linewidth=0, color=colourList[groupCount], zorder=100, alpha=0.3)
            ax2.set_ylabel('spearman rank p-value < ' + str(pvalboundary))
        if corvals==True:
            yvals = [spearmanr(x[rankcol],x[col])[0] for i,x in trialsdf.groupby(trialsdf.index.floor(RESAMPLE))]
            ax.plot(xvals, yvals, label=LABEL, linewidth=2, color=colourList[groupCount], zorder=100)

        groupCount+=1

    ax2.set_ylim(0,groupCount)
    ax2.set_yticklabels([])
    ax2.set_yticks([])
    #fig.autofmt_xdate()
    ax.set_xlabel('Time since stimulus onset (s)')#, fontsize='xx-small')
    ax.set_ylabel(YLABEL)#, fontsize='xx-small')
    ax.set_ylim(YLIM[0],YLIM[1])
    #ax.set_yticks([-1.0, 0, 1.0])
    ax.set_xlim(XLIM[0], XLIM[1])
    if grouping == 'coh':
        plt.legend(title='Coherence', fontsize='xx-small')
    elif grouping == 'trialID':
        pass
    else:
        plt.legend(title=grouping, fontsize='xx-small')
    plotnice()
    return fig


