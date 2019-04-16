from utilities import *
import os
import glob
import time
import datetime
import numpy
import imgstore

def checkDate(fn):
    if os.path.exists(fn):
        return datetime.datetime.fromtimestamp(os.path.getctime(fn))
    else:
        return np.nan

def collectProcessingStats(d):
    d = slashdir(d)
    
    list_of_files = glob.glob(d + '*.mp4') 
    latest_file = max(list_of_files, key=os.path.getctime)

    DATA = dict({
    'framecount': imgstore.new_for_filename(d+'metadata.yaml').frame_count,
    'recorded': getTimeFromTimeString(d.split('/')[-2].split('_',3)[-1].split('.')[0]),
    'stitchBegin': checkDate(d+'metadata.yaml'),
    'stitchEnd': checkDate(latest_file),
    'converted': checkDate(d+'track/converted.pv'),
    'tracked':checkDate(d+'track/converted.results'),
    'pickled': checkDate(d+'track/frameByFrameData.pickle')}
    )
    return DATA


def get_sorted(df, col1, col2):
    """
    returns to series, values from df[col1] and df[col2] sorted by col1
    """
    foo = df.sort_values(col1)
    return foo[col1], foo[col2]

def plot_cumulative(df):
    df.loc[:,'millFrames'] = df.loc[:,'framecount']/1000000.0
    columns = ['recorded','stitchEnd','converted','tracked']#,'pickled']
    labels = ['recorded','stitched','converted for tracking','tracked']#,'compiled']
    for i in range(len(columns)):
        foo = df[~np.isnat(df[columns[i]])]
        x, y = get_sorted(foo, columns[i], 'millFrames')
        plt.plot(x, y.cumsum(), label=labels[i])
    plt.legend()
    plt.xlabel('date')
    plt.ylabel('millions of frames')
    plt.show()
    #plt.close('all')
    return
    


 
 
df = pd.DataFrame()
for fn in glob.glob('/media/recnodes/recnode_2mfish/*dotbot*.stitched'):
    try:
        df = df.append(collectProcessingStats(fn), ignore_index=True)
        print "appended", fn.split('/')[-1]
    except Exception as E:
        print "ERROR: ", fn, E

plot_cumulative(df)
df.to_pickle('/home/dan/Desktop/processing_report.pickle')
plot_cumulative(df)
