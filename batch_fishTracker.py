#!/usr/bin/python


from __future__ import print_function
from __future__ import absolute_import
import glob
import run_fishTracker
import argparse
import os
import plot_positions
#import polarization_rotation
from utilities import *
#import count



from multiprocessing import Process
import traceback
#import fnmatch
#from multiprocessing import Process

def errorLogIt(E):
    errorLog = open(os.path.expanduser('~/setup_debian/FishTracker/Application/build/batchlog_batch.txt'), 'a')
    errorLog.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t')
    errorLog.write(vDir + '\t')
    errorLog.write('ERROR from batch_fishTracker' + '\n')
    errorLog.write(str(E) + '\n\n\n')
    errorLog.close()
    return


def convert_video_format(MAIN_DIR):
    FNULL = open(os.devnull, 'w')
    numFish = count.count_from_vid(MAIN_DIR + '/000000.mp4')
    vidSet = MAIN_DIR + '/%6d.mp4'
    track_dir = MAIN_DIR + '/track'
    launch_conversion = "~/setup_debian/FishTracker/Application/build/framegrabber -d '" + track_dir + "' -i '" + vidSet + "' -o converted.pv -settings conversion -nowindow"
    if not (os.path.exists(track_dir + '/converted.pv')):
        if os.path.exists(os.path.expanduser('~/setup_debian/FishTracker/Application/build/video_average.png')):
            os.remove(os.path.expanduser('~/setup_debian/FishTracker/Application/build/video_average.png'))
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '\t' ,"Running conversion on file: ", track_dir)
        try:
            subprocess.check_call([launch_conversion],stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
        
        except Exception as e:
            errorLog = open(os.path.expanduser('~/setup_debian/FishTracker/Application/build/batchlog.txt'), 'w')
            errorLog.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t')
            errorLog.write(track_dir + '\t')
            errorLog.write('error during conversion step' + '\n')
            errorLog.write(str(e) + '\n\n\n')
            errorLog.close()
            FNULL.close()
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'\t' ,"ERROR converting file: ", track_dir)
            return
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
    parser.add_argument('--exportNewData', type=bool, required=False, default=False,
                        help='make true to reload old files and export new npz files')
    parser.add_argument('--debug', type=bool, required=False, default=False,
                        help='make True to show window during tracking and conversion')
                
    args = parser.parse_args()
    
    HANDLE = args.handle.split(',')
    
    BKG_RULE = args.background
    
    DIRECTORIES = args.dir.split(',')
    for x in range(len(DIRECTORIES)):
        if DIRECTORIES[x][-1] != '/':
            DIRECTORIES[x] += '/'
    
    if os.path.exists(BKG_RULE):
        from . import utilities
        utilities.createBackgroundImage(BKG_RULE, method='mean') #FIXME when tristan updates
        mkBkg=False
    elif BKG_RULE == '0':
        mkBkg = False
    else:
        mkBkg = True
    
    numFish=0
    """
    # GET ALL FILES THAT ARE NOT CONVERTED
    fileList = []
    for term in HANDLE:
        for DIR in DIRECTORIES:
            for vDir in glob.glob(DIR + '*' + term + '*'):
                if (not os.path.exists(vDir + '/track/converted.results')):
                    fileList.append(vDir)
       
    # CONVERT MP4 TO PV IN PARALLEL (UP TO 32 ) #FIXME should detect number of processors
    threadcount = 0
    for filenum in np.arange(len(fileList)):
        vDir = fileList[filenum]
        try:
            
            try:
                numFish = count.count_from_vid(vDir + '/000000.mp4')
            except:
                numFish = 0
            print 'processing', vDir, 'fishcount: ', numFish
            
            p = Process(target=run_fishTracker.convert, args=(vDir,mkBkg, args.newonly, numFish))
            print "processing: ", vDir
            p.start()
            threadcount += 1
            
            if p.is_alive():
                if (threadcount >= 32) or (filenum == len(fileList)):
                    threadcount = 0
                    p.join()
        except Exception, e:
            errorLogIt(e)
            pass 
    """
    # TRACK, THEN RUN BASIC ANALYSIS
    for term in HANDLE:
        for DIR in DIRECTORIES:
            for vDir in glob.glob(DIR + '*' + term + '*' + '.stitched'):
                vDir = slashdir(vDir)
                _fishnum = int(vDir.split('/')[-2].split('_')[1])
                if not os.path.exists(vDir + 'track/converted.pv'):
                    if os.path.getsize(vDir + '000000.mp4') > 1000: #skip blank files...
                        run_fishTracker.setup_tristrack(vDir, _fishnum)
                        run_fishTracker.convert(vDir, mkBkg, args.newonly, _fishnum, args.debug)
                    
                if (not os.path.exists(vDir + 'track/converted.results')) and (os.path.exists(vDir + 'track/converted.pv')):
                    run_fishTracker.track(vDir, mkBkg, args.newonly, _fishnum, args.debug)
                elif (os.path.exists(vDir + 'track/converted.results')) and (os.path.exists(vDir + 'track/converted.pv') and (args.exportNewData)):
                    if not os.path.exists(vDir + 'track/fishTracker.settings'):
                        run_fishTracker.setup_tristrack(vDir, _fishnum)
                        run_fishTracker.track(vDir, mkBkg, args.newonly, _fishnum, args.debug)
                    elif getModTime(vDir + 'track/fishTracker.settings') < getTimeFromTimeString('20190315_130000'):
                        run_fishTracker.setup_tristrack(vDir, _fishnum)
                        run_fishTracker.track(vDir, mkBkg, args.newonly, _fishnum, args.debug)
                """    
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

    
    
    
    
    


            
            
