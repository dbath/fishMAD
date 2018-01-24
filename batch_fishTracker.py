#!/usr/bin/python


import glob
import run_fishTracker
import argparse
import os
import plot_positions
import polarization_rotation
from utilities import *
import count
#import fnmatch
#from multiprocessing import Process

def errorLogIt(E):
    errorLog = open(os.path.expanduser('~/FishTracker/Application/build/batchlog_batch.txt'), 'a')
    errorLog.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t')
    errorLog.write(vDir + '\t')
    errorLog.write('ERROR from batch_fishTracker' + '\n')
    errorLog.write(str(E) + '\n\n\n')
    errorLog.close()
    return


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=False, default = '/media/recnodes/kn-crec05,/media/recnodes/kn-crec06,/media/recnodes/kn-crec07',help='path to directory')
    parser.add_argument('--handle', type=str, required=False, default='_dotbot_,_jwj_', 
                        help='provide unique identifier (or comma-separated list) to select a subset of directories.')
    parser.add_argument('--background', type=str, required=False, default='0',
                        help="provide an path or integer descrbing how to handle backgrounds.  path:'\t'Generate a background image from the given directory and use it repeatedly. '\n'0:'\t'use pre-existing.'\n'1:'\t'create one, then use it repeatedly.'\n'>1:'\t'create a new bkg for every video.")
    parser.add_argument('--newonly', type=bool, required=False, default=True,
                        help='make false to retrack and save over old data')
                
    args = parser.parse_args()
    
    HANDLE = args.handle.split(',')
    
    BKG_RULE = args.background
    
    DIRECTORIES = args.dir.split(',')
    for x in range(len(DIRECTORIES)):
        if DIRECTORIES[x][-1] != '/':
            DIRECTORIES[x] += '/'
    
    if os.path.exists(BKG_RULE):
        import utilities
        utilities.createBackgroundImage(BKG_RULE, method='mean') #FIXME when tristan updates
        mkBkg=False
    elif BKG_RULE == '0':
        mkBkg = False
    else:
        mkBkg = True
    
    numFish=0
    for term in HANDLE:
        for DIR in DIRECTORIES:
            for vDir in glob.glob(DIR + '*' + term + '*'):
                vDir = slashdir(vDir)
                if '_256_' in vDir:
                    continue
                if HANDLE != '_jwj_':
                    if (not os.path.exists(vDir + '/track/converted.results')):
                        try:
                            print "counting:", vDir
                            numFish = count.count_from_vid(vDir + '/000000.mp4')
                            print str(numFish), " fish detected."
                        except Exception, e:
                            errorLogIt(e)
                            pass
                if (not os.path.exists(vDir + '/track/converted.results')):
                    try:
                        print "executing run_fishTracker.py on:", vDir
                        run_fishTracker.doit(vDir, mkBkg, args.newonly, numFish)
                        print "tracking successful"
                    except Exception, e:
                        errorLogIt(e)
                        pass
                if HANDLE != '_jwj_':
                    if (not os.path.exists(vDir + '/track/frameByFrame_complete')):
                        try:
                            fbf = getFrameByFrameData(vDir + '/track', RESUME=False)
                            print ".got frame by frame data", vDir
                        except Exception, e:
                            errorLogIt(e)
                            continue
                    if (not os.path.exists(vDir + '/track/positions.png')):
                        try:
                            plot_positions.plot_positions(vDir)
                            print "..got position plots", vDir
                        except Exception, e:
                            errorLogIt(e)
                            pass
                    if (not os.path.exists(vDir + '/track/density_meandRotation-x_polarization-y.png')):
                        try:
                            polarization_rotation.run(vDir)
                            print "...got rotation & polarization data", vDir
                        except Exception, e:
                            errorLogIt(e)
                            pass
                        

    """
    threadcount = 0
    _filelist = []
    for term in HANDLE:
        for vDir in glob.glob(DIR + '*' + term + '*'):
            if (not os.path.exists(vDir + '/track/converted.results')) or not args.newonly:
                _filelist.append(_directory)
    
    for directory in np.arange(len(_filelist)): 
        print 'executing run_fishTracker.py on: ' , _filelist[directory]
        
        p = Process(target=run_fishTracker.doit, args=(vDir, mkBkg, args.newonly))
        p.start()
        threadcount+=1

        if p.is_alive():
            if threadcount >=4:
                threadcount = 0
                p.join()
            elif _filelist[directory] == _filelist[-1]:
                threadcount=0
                p.join()


        if BKG_RULE == '1':
            mkBkg = False

        """
    
    
    
    
    
    


            
            
