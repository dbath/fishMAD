
import glob
import argparse
import os
import plot_positions
import polarization_rotation
from utilities import *
import count
from multiprocessing import Process
import traceback


def errorLogIt(E):
    errorLog = open(os.path.expanduser('~/FishTracker/Application/build/batchlog_batch.txt'), 'a')
    errorLog.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t')
    errorLog.write(vDir + '\t')
    errorLog.write('ERROR from batch_rotation' + '\n')
    errorLog.write(str(E) + '\n\n\n')
    errorLog.close()
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=False, default = '/media/recnodes/kn-crec05,/media/recnodes/kn-crec06,/media/recnodes/kn-crec07',help='path to directory')
    parser.add_argument('--handle', type=str, required=False, default='_dotbot_,_jwj_', 
                        help='provide unique identifier (or comma-separated list) to select a subset of directories.')

                
    args = parser.parse_args()
    
    HANDLE = args.handle.split(',')
    
    
    DIRECTORIES = args.dir.split(',')
    for x in range(len(DIRECTORIES)):
        if DIRECTORIES[x][-1] != '/':
            DIRECTORIES[x] += '/'
        
    fileList = []
    for term in HANDLE:
        for DIR in DIRECTORIES:
            for x in glob.glob(DIR + '*' + term + '*'):
                fileList.append(x)
    threadcount = 0
    for filenum in np.arange(len(fileList)):
        vDir = fileList[filenum]
        if not os.path.exists(vDir + '/track/density_meandRotation-x_polarization-y.png'):
            if os.path.exists(vDir + '/track/frameByFrame_complete'):
                try:
                    p = Process(target=polarization_rotation.run, args=(vDir,))
                    p.start()
                    print "processing: ", vDir
                    threadcount += 1
                    
                    if p.is_alive():
                        if (threadcount >= 32) or (filenum == len(fileList)):
                            threadcount = 0
                            p.join()

                except Exception, e:
                    errorLogIt(e)
                    pass        



