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
    columns = ['recorded','stitchEnd','tracked']#,'pickled']
    labels = ['recorded','stitched','tracked']#,'compiled']
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
print "DONE WITH LARGE TANK DATA"

df = pd.DataFrame()
for DIR in ['kn-crec05','kn-crec06','kn-crec07']:
    for fn in glob.glob('/media/recnodes/' + DIR + '/coherencetestangular_*'):
        try:
            df = df.append(collectProcessingStats(fn), ignore_index=True)
            print "appended", fn.split(',')[-1]
        except Exception as E:
            print "ERROR: ", fn, E

plot_cumulative(df)
df.to_pickle('/home/dan/Desktop/processing_report_smalltanks.pickle')


print "DONE"


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

def getTrackingStats(fn):
    d = np.load(fn)
    f =  pd.DataFrame([d[x] for x in d.iterkeys()]).T   
    f.columns = d.keys()
    N = []
    T = []
    for i in range(len(f['stats'][0])):
        N.append(f['stats'][0][i][2])
        data = f['stats'][0][i]
        T.append(data[0] + data[1] + data[3] + data[4])
    return pd.DataFrame({'N':N,'T': T})
        
df = pd.DataFrame()
nFish = []
tTrack = []
for DIR in ['kn-crec05','kn-crec06','kn-crec07','recnode_2mfish']:
    for fn in glob.glob('/media/recnodes/'+DIR+'/*dotbot*/track/fishdata/converted_statistics.npz'):
        try:
            newdf = getTrackingStats(fn)
            newdf['groupsize'] = int(fn.split('/')[-4].split('_')[-4])
            df = pd.concat([df, newdf], axis=0)
            print "appended", fn.split('/')[-4]
        except Exception as E:
            print "ERROR: ", fn, E

df['FPS'] = 1.0/df['T']
g = df.groupby('groupsize')            
plt.plot(g['N'].mean(), g['FPS'].mean())

plt.errorbar(g['N'].mean(), g['FPS'].mean(), 
             xerr=g['N'].std(), yerr=g['FPS'].std(), 
             capsize=4, linestyle='None')
plotnice()             
plt.xlabel('Group size')
plt.ylabel('Tracking rate (frames/second)')
