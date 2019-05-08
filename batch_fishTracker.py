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
        utilities.createBackgroundImage(BKG_RULE, method='mode') 
        mkBkg=False
    elif BKG_RULE == '0':
        mkBkg = False
    else:
        mkBkg = True
    
    numFish=0

    # TRACK, THEN RUN BASIC ANALYSIS

    
    for term in HANDLE:
        for DIR in DIRECTORIES:    
            if '2mfish' in DIR:
                searchterm = DIR + '*' + term + '*' + '.stitched'
            else:
                searchterm = DIR + '*' + term + '*'
            for vDir in glob.glob(searchterm):
                vDir = slashdir(vDir)
                _fishnum = int(vDir.split('/')[-2].split('_')[1])
                
                #catch all that have not been converted
                if not os.path.exists(vDir + 'track/converted.pv'):
                    if os.path.getsize(vDir + '000000.mp4') > 1000: #skip blank files...
                        run_fishTracker.setup_tristrack(vDir, _fishnum)
                        run_fishTracker.convert(vDir, mkBkg, args.newonly, _fishnum, args.debug)
                #catch all that have been converted but not tracked
                if (not os.path.exists(vDir + 'track/converted.results')):
                    if (os.path.exists(vDir + 'track/converted.pv')):
                        run_fishTracker.track(vDir, mkBkg, args.newonly, _fishnum, args.debug)
                #catch all that have been converted and tracked but data is gone (ex for re-export)
                if os.path.exists(vDir + 'track/fishdata'):
                    if len(os.listdir(vDir + 'track/fishdata') ) == 0: #tracking data was deleted for re-export
                        run_fishTracker.track(vDir, mkBkg, args.newonly, _fishnum, args.debug)
                
