
import matplotlib.pyplot as plt

from matplotlib.gridspec import GridSpec
import pandas as pd
import numpy as np
import imgstore
from utilities import *
import stim_handling as stims
import scipy
from scipy.signal import find_peaks



groupsizes = [4,8,16,32,64,128,256,512,1024]
coherences = [0.0,0.2,0.4,0.6,0.8,1.0]

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


allData = pd.read_pickle('/media/recnodes/Dan_storage/20200120_coherence_data_compiled_full.pickle' )
allData['groupsize'] = allData['groupsize'].astype(int)
allData['coh'] = np.around(allData['coh'],1)
g = allData.groupby(['groupsize','coh'])
fig = plt.figure()
#gs = GridSpec(len(groupsizes),len(coherences), figure=fig)
gs = GridSpec(len(coherences),len(groupsizes), figure=fig)#FIXME
peakDF = pd.DataFrame()
XLIM = (150,300)
gaussian_X = np.linspace(-0.6,0.6,201)
BIN_WIDTH = 0.08
bins=np.arange(0,5,BIN_WIDTH)
col='entropy_Ra'#'median_dRotation_cArea'
for groupsize in groupsizes:
    for coherence in coherences:

        data = g.get_group((groupsize,coherence))
        
        data = data.loc[data.syncTime.between(np.timedelta64(XLIM[0],'s'), np.timedelta64(XLIM[1],'s')), :]
        #data[col] *= -1.0  
        
        pertrial = list()
        for trialID, vals in data.groupby('trialID'):
            _hist, _bins = np.histogram(vals[col], bins=bins, density=True)
            pertrial.append(_hist)
        meds = np.median(np.stack(pertrial), axis=0)#.mean(axis=0)
        z = np.quantile(np.stack(pertrial),0.05, axis=0)
        first = np.quantile(np.stack(pertrial),0.25, axis=0)
        third = np.quantile(np.stack(pertrial), 0.75, axis=0)
        hundo = np.quantile(np.stack(pertrial),0.95, axis=0)
        
        #ax = fig.add_subplot(gs[len(groupsizes)-1-groupsizes.index(groupsize),coherences.index(coherence)])
        ax = fig.add_subplot(gs[len(coherences)-1-coherences.index(coherence),groupsizes.index(groupsize)])
        if ax.is_first_col():
            ax.set_ylabel(str(coherence))
        if ax.is_first_row():
            ax.set_title(str(groupsize))
        #ax.fill_between(bins[:-1], z, hundo, color='#CC33CC90')
        ax.fill_between(bins[:-1], first, third, color='#3333CC90')
        ax.plot(bins[:-1],meds, color='k', linewidth=1)
        #ax.set_ylim(0,25)
        if not ax.is_last_row():
            ax.axes.get_xaxis().set_ticks([])
        if not ax.is_first_col():
            pass#ax.axes.get_yaxis().set_ticks([])
        plotnice(plotType='hist', ax=ax)
plt.show()
