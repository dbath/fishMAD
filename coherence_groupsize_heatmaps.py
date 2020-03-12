
import matplotlib.pyplot as plt

from matplotlib.gridspec import GridSpec
import pandas as pd
import numpy as np
import imgstore
from utilities import *
import stim_handling as stims
import scipy
from scipy.signal import find_peaks

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


def sync_by_stimStart(df, col='speed'):
    """
    pass a df with stim information
    returns the df with rotation values adjusted for direction so rotation of new stim is positive
    """
    df = df.sort_values('Timestamp').reset_index()
    #df = df[:-10] #drop end to avoid dealing with annoying NaN cases #lazy #FIXME
    
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
    if len(alignPoints) > 0:
        i = alignPoints[0]
    else:
        i = df.iloc[0]['Timestamp']
    trials = pd.DataFrame()
    trialID = 0        
    #i = alignPoints[0]#for i in alignPoints:
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
        
def plot_many_trials(trials, col='median_dRotation_cArea', grouping='trialID', plotTrials=True, fig= None, ax=None, colour=None, XLIM=(-30,400), YLIM=(-1.05,1.05),RESAMPLE='1s', NORMALIZE_PRESTIM=False, YLABEL='Mean congruent rotation order $\pm$ SEM', statistic='mean'):
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
            if statistic == 'mean':
                r = data.resample(RESAMPLE).mean()
            elif statistic == 'std':
                r = data.resample(RESAMPLE).std()
            sem = 1.253*(data.resample(RESAMPLE).std())/np.sqrt(N) #http://davidmlane.com/hyperstat/A106993.html and
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
                            alpha=0.05, 
                            linewidth=0,
                            zorder=10)
            groupCount+=1

    #fig.autofmt_xdate()
    ax.set_xlabel('Time since stimulus onset (s)')#, fontsize='xx-small')

    
    if NORMALIZE_PRESTIM:
        ax.set_ylabel('Normalized ' + YLABEL)#, fontsize='xx-small')
    else:
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



import matplotlib.colors as mcolors

def plot_hist(trials, col='median_dRotation_cArea', grouping='trialID', plotTrials=True, fig= None, ax=None, XLIM=(-30,400), BIN_WIDTH=0.01):
    colourList = ['#EA4335','#E16D13','#FBBC05','#34A853','#4285F4','#891185',
                  '#4285F4','#FBBC05','#34A853','#EA4335','#891185','#E16D13','#0B1C2E','#347598']


    trials = trials.loc[trials.syncTime.between(np.timedelta64(XLIM[0],'s'), np.timedelta64(XLIM[1],'s')), :]



    if fig== None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    if 'Rotation' in col:
        bins=np.arange(-1.1,1.1,BIN_WIDTH)
    else:
        bins=np.arange(-0.6,0.6,BIN_WIDTH)

    clist = [(0, "red"), (0.125, "red"), (0.25, "orange"), (0.5, "green"), 
             (0.7, "green"), (0.75, "blue"), (1, "blue")]
    rvb = mcolors.LinearSegmentedColormap.from_list("", clist)
    if grouping == 'dontgroup':
        g = trials.copy()
    else:
        g = trials.groupby(grouping).median()
    _bars, _bins, _patches = plt.hist(g[col], bins=bins, density=True)
    fracs = _bins/_bins.max()
    norm = mcolors.Normalize(fracs.min(), fracs.max())
    
    for thisfrac, thispatch in zip(fracs, _patches):
        color = plt.cm.viridis(norm(thisfrac))
        thispatch.set_facecolor(color)
        
    #ax.bar(bins[1:], heights, color=rvb(np.arange(len(bins)).astype(float)/float(len(bins)))[1:], width=0.1)
    #ax.set_ylim(0,1.0/BIN_WIDTH)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_yticks([])

    #plotnice(plotType='hist')
    return _bars, _bins

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
 


def beta_transform(x):
    """
    From Jake Graving. If this is wrong it's his fault. 
    
    x is a series or df column, where the data are bounded
    """

    EPSILON = np.finfo(np.float64).eps
    x = (x + 1.0) / 2.0 # normalize to [0, 1] 
    x = np.clip(x, EPSILON, 1.0 - EPSILON) # clip to (0, 1) 
    return x
 

def get_beta_pdf(datacol, _min=0, _max=1, NBINS=100):
    (a,b, lowLimit, Scale) = scipy.stats.beta.fit(datacol, _min, _max)   
    x = np.linspace(scipy.stats.beta.ppf(0.01, a, b), beta.ppf(0.99, a, b), NBINS)
    y = scipy.stats.beta.pdf(x,a,b)
    return x, y

groupsizes = [4,8,16,32,64,128,256,512,1024]
coherences = [0.0,0.2,0.4,0.6,0.8,1.0]

allData = pd.read_pickle('/media/recnodes/Dan_storage/20200120_coherence_data_compiled_full.pickle' )
allData['groupsize'] = allData['groupsize'].astype(int)
allData['coh'] = np.around(allData['coh'],1)
g = allData.groupby(['groupsize','coh'])
fig = plt.figure()
gs = GridSpec(len(groupsizes),len(coherences), figure=fig)
peakDF = pd.DataFrame()
XLIM = (20,300)
gaussian_X = np.linspace(-0.6,0.6,201)
BIN_WIDTH = 0.012
col='entropy_normed_base'
for groupsize in groupsizes:
    for coherence in coherences:
        try:
            data = g.get_group((groupsize,coherence))
            
            data = data.loc[data.syncTime.between(np.timedelta64(XLIM[0],'s'), np.timedelta64(XLIM[1],'s')), :]
            #data[col] *= -1.0  
            
            distrib_X = np.linspace(-0.6,0.6,1.0/BIN_WIDTH)         
            try:
                peakdata = scipy.stats.gaussian_kde(data[col]).pdf(distrib_X)
                peaks, peakParams = scipy.signal.find_peaks(peakdata,0)
                FWHM = scipy.signal.peak_widths(peakdata, peaks, rel_height=0.5, prominence_data=None, wlen=None)


            except:
                peaks = []
                peakParams = []
                
            if len(peaks) == 0:
                Peak_1 = np.nan
                PeakHeight_1 = np.nan
                Peak_1_fwhm = np.nan
                Peak_2 = np.nan
                PeakHeight_2 = np.nan
                Peak_2_fwhm = np.nan
            elif len(peaks) < 2:
                Peak_1 = gaussian_X[peaks[peakParams['peak_heights'].argmax()]]
                PeakHeight_1 = peakParams['peak_heights'].max()
                Peak_1_fwhm = FWHM[0][peakParams['peak_heights'].argmax()]
                Peak_2 = np.nan
                PeakHeight_2 = np.nan
                Peak_2_fwhm = np.nan
            else:
                first, second = pd.DataFrame(peakParams)['peak_heights'].nlargest(2).index
                Peak_1 = gaussian_X[peaks[first]]
                PeakHeight_1 = peakParams['peak_heights'][first]
                Peak_1_fwhm = FWHM[0][first]
                Peak_2 = gaussian_X[peaks[second]]
                PeakHeight_2 = peakParams['peak_heights'][second]      
                Peak_2_fwhm = FWHM[0][second]      

            ax = fig.add_subplot(gs[groupsizes.index(groupsize),coherences.index(coherence)])

            plot_hist(data, col=col, grouping='dontgroup', plotTrials=True, fig= fig, ax=ax, XLIM=XLIM, BIN_WIDTH=BIN_WIDTH)
            #Find centroid of PDF of rotation scores fit to gaussian

            row = pd.Series({'coherence':coherence,
                 'groupsize':groupsize,
                 'mode_R':bins[freqs.argmax()],
                 'mode_R_height':freqs.max(),
                 'pdfPeak1':Peak_1,
                 'pdfPeak2':Peak_2,
                 'pdfPeak1_height':PeakHeight_1,
                 'pdfPeak2_height':PeakHeight_2,
                 'pdfPeak1_fwhm':Peak_1_fwhm,
                 'pdfPeak2_fwhm':Peak_2_fwhm
                 }, name=(groupsize,coherence))
            peakDF = peakDF.append(row)
        except:
            continue
print 'mode height'
print peakDF.groupby(['groupsize','coherence'])['mode_R_height'].mean().unstack()
print '\n pdfPeak1_height'
print peakDF.groupby(['groupsize','coherence'])['pdfPeak1_height'].mean().unstack()
print '\n pdfPeak1'
print peakDF.groupby(['groupsize','coherence'])['pdfPeak1'].mean().unstack()

plt.show()

cols = ['pdfPeak1','pdfPeak1_height','pdfPeak1_fwhm']
titles = ['Peak entropy', 'Peak height', 'FWHM']

cols = ['median_dRotation_cArea','std_dRotation_cArea','entropy_Ra']
titles = ['median','std','entropy']
R=1
S=0

#def plotent(S, R):
_fig = plt.figure()
for i in range(3):
    axi = _fig.add_subplot(1,3,i+1)
    heatmap(catdata.groupby(['prestimAreaGroup','coh'])[cols[i]].mean().unstack(), 
               RESIZE_FACTOR=R, SIGMA=S,
               fig=_fig, ax=axi)
    axi.set_ylabel('Group Size')
    axi.set_xlabel('Coherence')
    axi.set_title(titles[i])
    axi.spines['top'].set_visible(False)
    axi.spines['right'].set_visible(False)
plt.show()
#    return





