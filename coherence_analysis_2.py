

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


from scipy.interpolate import splrep, splev

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

        
groupData = pd.DataFrame()
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
        groupData = pd.concat([groupData,newdf], axis=0)
    except:
        print "FAILED"
        pass
    
groupData.to_pickle('/media/recnodes/Dan_storage/190625_groupdata_coherence_analysis_2.pickle')

prestim = groupData.loc[groupData['syncTime'] < np.timedelta64(0), :]
g = prestim.groupby(['trialID']) 
m = g['Orotation'].median()   
revlist = list(m[m < -0.5].index)
revData = groupData[groupData['trialID'].isin(revlist)]




