from scipy.interpolate import splrep, splev 
import scipy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def smooth(x, y, factor):
    spl = scipy.interpolate.UnivariateSpline(x, y)
    spl.set_smoothing_factor(factor)
    return spl(x)

def set_threshold(gd, THRESHOLD, COL):
    gd.loc[gd[COL] <= 0.95*THRESHOLD, 'correct'] = 0
    gd.loc[gd[COL] > 1.05*THRESHOLD, 'correct'] = 1
    gd.loc[gd[COL] > 1.05*THRESHOLD, 'incorrect'] = 0
    gd.loc[gd[COL] <= 0.95*THRESHOLD, 'incorrect'] = 1
    gd['responding'] = gd['correct'] + gd['incorrect']
    gd.loc[gd['responding'] > 0, 'responding'] = 1 
    return gd

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
            r = data.resample(RESAMPLE).mean()
            sem = 1.253*(data.resample(RESAMPLE).std()/np.sqrt(N)) #http://davidmlane.com/hyperstat/A106993.html and
            #    https://influentialpoints.com/Training/standard_error_of_median.htm
            try:
                count = data.resample(RESAMPLE).count()
                removeLowDataCount = count[col] <= 0.2*count[col].max()
                r[removeLowDataCount] = np.nan
                sem[removeLowDataCount] = np.nan
            except:
                pass
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
    return fig



from scipy.ndimage.filters import gaussian_filter
from skimage.transform import resize 
from mpl_toolkits.axes_grid1 import make_axes_locatable

def heatmap(df, fig=None, ax=None, SIGMA=0, RESIZE_FACTOR=1):
    """
    pass a 2d dataframe (for example, df.groupby([col1,col2])[col3].mean().unstack() )
    
    returns a heatmap as an imshow image with optional smoothing (sigma, resizing)
    """
    if fig == None:
        fig = plt.figure()
    if ax == None:
        ax = fig.add_subplot(111)
    img = np.array(df)
    resized = resize(img, (img.shape[0]*RESIZE_FACTOR, img.shape[1]*RESIZE_FACTOR))
    filtered_img = gaussian_filter(resized, SIGMA)
    plt.sca(ax)
    #show image
    im = ax.imshow(filtered_img)
    #create colourbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(im, cax=cax)
    return




def get_kinetics(groupData, col='median_dRotation_cArea', THRESHOLD=0.75):
    groupData.coh = np.around(groupData.coh, 1)
    

    g = groupData.groupby('trialID')

    _RT = []
    bouts = pd.DataFrame()
    trialCount = 0
    correctCount = 0
    for trial, data in g:
        data = data.copy()


        trialCount +=1

        data['smoothed'] = smooth(data.Timestamp, data[col], 110) #FIXME hardcoded smoothing value

        data = set_threshold(data, THRESHOLD, 'smoothed')

              
        stim_period = data.loc[data['syncTime'].between(np.timedelta64(0), np.timedelta64(300,'s')),:]#FIXME hardcoded stim duration
        

        
        #_RT.append(stim_period.loc[stim_period['correct'].idxmax(), 'syncTime'].total_seconds())
        post_stim = data.loc[data['syncTime'] > np.timedelta64(300,'s')] #FIXME hardcoded time

        bout = get_bouts(stim_period)
        md = data.iloc[0] #metadata
        bout['trialID'] = md.trialID
        bout['prior'] = THRESHOLD
        bout['coh'] = md.coh
        bout['groupsize'] = md.groupsize
        try:
            if stim_period['correct'].mean() > 0.5: #FIXME so much thresholding
                bout['correctTrial'] = 1.0
            else:
                bout['correctTrial'] = 0.0
            bout['RT'] = stim_period.loc[stim_period['correct'].idxmax(), 'syncTime'].total_seconds()
            bout['DecayTime'] = post_stim.loc[post_stim['correct'].idxmin(), 'syncTime'].total_seconds()

            bouts = pd.concat([bouts, bout], axis=0)
        except:
            print "FAILED AT RT AND DECAY TIME", md.trialID
    bouts = bouts.loc[(10.0*bouts['coh'])%2 ==0, :]
    bouts['groupsize'] = bouts['groupsize'].astype(int)
    bouts['coh'] = bouts['coh'].astype(np.float64)

        
    bouts.to_pickle('/media/recnodes/Dan_storage/20200207_bouts_of_rotation.pickle')
    return bouts

def rank_on_column(df, col, nRanks):
    """
    pass a df, returns an index-matched series grouping col into nRanks groups
    """
    bounds = np.linspace(0,1,nRanks+1)
    df = df.copy()
    df['rank'] = np.nan
    for i in range(nRanks):
        if i == 0:
            INKL=True
        else:
            INKL=False
        df.loc[df[col].between(df.quantile(bounds[i])[col], 
                               df.quantile(bounds[i+1])[col] + 1e5, #tiny hack for inclusive upper bound
                               inclusive=INKL),
              'rank'] = i
    return df['rank']


def sync_by_RT(df):
    g = df.groupby('trialID')
    newdf = pd.DataFrame()
    for ID, h in g:
        if h['correct'].sum() == 0:
            continue
        pre = h.loc[h['syncTime'] < np.timedelta64(0), :]
        if pre['median_dRotation_cArea'].mean() > 0: #remove trials where response is ambiguous
            continue

        h['sync_by_RT'] = h['syncTime'] - h.loc[h[h['syncTime'] > np.timedelta64(0)]['correct'].idxmax(), 'syncTime']
        post = h.loc[h['syncTime'] > np.timedelta64(0)]
        newdf = pd.concat([newdf, post], axis=0)
    return newdf
    
allData = pd.read_pickle('/media/recnodes/Dan_storage/20200120_coherence_data_compiled_full.pickle' )

#allData['syncTime'] -= np.timedelta64(6,'s')
prestim = allData.loc[allData['syncTime'] < np.timedelta64(0,'s'),:]       
m = prestim.groupby('trialID').mean()  

#for gs in list(set(allData.groupsize)):                                                           
#    m.loc[m.groupsize == gs, 'rank'] = rank_on_column(m.loc[m.groupsize==gs,:], 'median_dRotation_cArea', 2)
m['rank'] = 1.0
m.loc[m['median_dRotation_cArea'] < -0.1,'rank'] = 0.0

merge = allData.merge(m.reset_index()[['rank', 'trialID']], left_on='trialID', right_on='trialID')
g = merge.groupby('rank') 
reps = g.get_group(0.0) 
_THRESHOLD = 0.5
big = reps.loc[reps['groupsize'] > 50, :]
valdict = dict()
for T in np.linspace(0,1,21):
    bouts = get_kinetics(big, THRESHOLD=T)
    meancor = bouts.groupby('coh')['correctTrial'].mean()
    valdict[T] = list(meancor.values)
    plt.plot(meancor.index, meancor, label=str(T))
plt.legend()
plt.show()       
    
#bouts = get_kinetics(reps, THRESHOLD=_THRESHOLD)

meancor = bouts.groupby('coh')['correctTrial'].mean()
plt.scatter(meancor.index, meancor)
plt.show() 
rt = reps.merge(bouts[['trialID','RT','correctTrial']], left_on='trialID', right_on='trialID')
rt = rt.loc[rt['correctTrial'] == 1,:]
rt = set_threshold(rt, 0.25, 'median_dRotation_cArea')
rt = sync_by_RT(rt)
#rt['sync_by_RT'] = rt['syncTime'] - pd.to_timedelta(rt['RT'], unit='s')

big = rt.loc[rt['groupsize'] > 50, :]
plot_by_RT(big, col='median_dRotation_cArea', grouping='coh', plotTrials=False, RESAMPLE='250ms')
plt.show()
bouts['DecayTime'] -= 300.0
cols = ['DecayTime','RT','correctTrial']
titles = ['Decay Time (s)','Reaction Time (s)',' % Correct']
R=1
S=0

#def plotent(S, R):
_fig = plt.figure()
for i in range(3):
    axi = _fig.add_subplot(1,3,i+1)
    heatmap(bouts.groupby(['groupsize','coh'])[cols[i]].mean().unstack(), 
               RESIZE_FACTOR=R, SIGMA=S,
               fig=_fig, ax=axi)
    axi.set_ylabel('Group Size')
    axi.set_xlabel('Coherence')
    axi.set_title(titles[i])
    axi.spines['top'].set_visible(False)
    axi.spines['right'].set_visible(False)
plt.show()



    
