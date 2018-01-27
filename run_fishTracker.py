#!/usr/bin/python


import imgstore
import os
import numpy as np
import shutil
import subprocess
import argparse
import scipy.misc
import datetime


def replace_background(_main_dir):
    if os.path.exists(_main_dir + 'track/video_average.png'):
        shutil.copy(_main_dir + 'track/video_average.png',
                    os.path.expanduser('~/FishTracker/Application/build/video_average.png'))
        print "retrieved previous background image"
    else:
        
        #create new background image
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '\t' ,"generating background image..."
        import utilities
        bkg = utilities.createBackgroundImage(_main_dir, 'mean')  #FIXME change to mode after tristan fixes
        scipy.misc.imsave(os.path.expanduser('~/FishTracker/Application/build/video_average.png'), bkg)
        scipy.misc.imsave(_main_dir + 'track/video_average.png', bkg)
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '\t' ,"got new background..."
    return

def convert(_main_dir, _make_bkg, NEW_ONLY, fishnum):
    MAIN_DIR = _main_dir
    if MAIN_DIR[-1] != '/':
        MAIN_DIR += '/'
    track_dir = MAIN_DIR + 'track'
    if not os.path.exists(track_dir):
        os.makedirs(track_dir)
    
    if (NEW_ONLY) and (os.path.exists(track_dir + 'converted.results')):
        return
    
    if _make_bkg == True:
        replace_background(MAIN_DIR)

    #copy default settings files and make fishdata dir

    if not os.path.exists(track_dir + 'fishTracker.settings'):
        if '_jwj_' in MAIN_DIR:
            shutil.copy(os.path.expanduser('~/fishMAD/tristrack_defaults/fishTracker_stickleback.settings'), track_dir + '/fishTracker.settings')
        else:
            shutil.copy(os.path.expanduser('~/fishMAD/tristrack_defaults/fishTracker.settings'), track_dir + '/fishTracker.settings')
    if not os.path.exists(track_dir + 'conversion.settings'):
        if '_jwj_' in MAIN_DIR:
            shutil.copy(os.path.expanduser('~/fishMAD/tristrack_defaults/conversion_stickleback.settings'), track_dir + '/conversion.settings')
        else:
            shutil.copy(os.path.expanduser('~/fishMAD/tristrack_defaults/conversion.settings'), track_dir + '/conversion.settings')
    if not os.path.exists(track_dir + '/fishdata'):
        os.makedirs(track_dir + '/fishdata')

    print "set up tristrack environment..."
    #Get metadata from videos
    store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml' )
    FPS = store.user_metadata['acquisitionframerate']
    videoSize =store.image_shape


    if (fishnum == 0) or (fishnum == None):
        #Get number of fish from MAIN_DIR filename.
        fishnum = int(MAIN_DIR.split('/')[-2].split('_')[1])
    if fishnum <= 5:
        fishnum += 2
    elif fishnum <= 15:
        fishnum += 4
    elif fishnum <= 55:
        fishnum += 6
    elif fishnum <= 100:
        fishnum += 10
    elif fishnum <= 200:
        fishnum += 15
    else:
        fishnum += 25

    #  customize conversion.settings
    openFile = open(track_dir + '/conversion.settings', 'r+b')
    SETTINGS = openFile.readlines()
    for item in SETTINGS:
        if item.find('frame_rate') != -1:
            framerate_loc = SETTINGS.index(item)
        if item.find('cam_framerate') != -1:
            camFrameRate_loc = SETTINGS.index(item)
        if item.find('cam_resolution') != -1:
            vidSize_loc = SETTINGS.index(item)
    SETTINGS[framerate_loc] = 'frame_rate = ' + str(FPS) + '\n'
    SETTINGS[camFrameRate_loc] = 'cam_framerate = ' + str(FPS) + '\n'  
    SETTINGS[vidSize_loc] = 'cam_resolution = ' + str([videoSize[0],videoSize[1]]) + '\n'
    # return pointer to top of file so we can re-write the content with replaced string
    openFile.seek(0)
    # clear file content 
    openFile.truncate()
    # re-write the content with the updated content
    openFile.write(''.join(SETTINGS))
    openFile.close()

    print "wrote new conversion file..."
    # Customize fishTracker.settings

    #   get and read tracker settings
    openFile = open(track_dir + '/fishTracker.settings', 'r+b')
    SETTINGS = openFile.readlines()
    for item in SETTINGS:
        if item.find('frame_rate') != -1:
            framerate_loc = SETTINGS.index(item)
        if item.find('number_fish') != -1:
            fishNum_loc = SETTINGS.index(item)
        if item.find('output_dir') != -1:
            outDir_loc = SETTINGS.index(item)
        if item.find('fish_minmax_size') != -1:
            fishSize_loc = SETTINGS.index(item)
    SETTINGS[framerate_loc] = 'frame_rate = ' + str(FPS) + '\n'
    SETTINGS[fishNum_loc] = 'number_fish = ' + str(fishnum) + '\n'  
    SETTINGS[outDir_loc] = 'output_dir = "' + track_dir + '"\n'
    if 'juvenile' in MAIN_DIR:
        SETTINGS[fishSize_loc] = "fish_minmax_size = [0.5,7]"
    # return pointer to top of file so we can re-write the content with replaced string
    openFile.seek(0)
    # clear file content 
    openFile.truncate()
    # re-write the content with the updated content
    openFile.write(''.join(SETTINGS))
    openFile.close()

    print "wrote new settings file..."

    FNULL = open(os.devnull, 'w')

    # Launch conversion
    vidSet = MAIN_DIR + '%6d.mp4'
    launch_conversion = "~/FishTracker/Application/build/framegrabber -d '" + track_dir + "' -i '" + vidSet + "' -o converted.pv -settings conversion -nowindow"
    if not (os.path.exists(track_dir + '/converted.pv')):
        if os.path.exists(os.path.expanduser('~/FishTracker/Application/build/video_average.png')):
            os.remove(os.path.expanduser('~/FishTracker/Application/build/video_average.png'))
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '\t' ,"Running conversion on file: ", track_dir
        try:
            subprocess.check_call([launch_conversion],stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
        except Exception, e:
            errorLog = open(os.path.expanduser('~/FishTracker/Application/build/batchlog.txt'), 'w')
            errorLog.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t')
            errorLog.write(track_dir + '\t')
            errorLog.write('error during conversion step' + '\n')
            errorLog.write(str(e) + '\n\n\n')
            errorLog.close()
            FNULL.close()
            print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'\t' ,"ERROR converting file: ", track_dir
            return
    FNULL.close()

    return

def track(_main_dir, _make_bkg, NEW_ONLY, fishnum):
    MAIN_DIR = slashdir(_main_dir)
    track_dir = MAIN_DIR + 'track'
    # Launch tracker
    FNULL = open(os.devnull, 'w')    
    if not (os.path.exists(track_dir + '/converted.results')):
        shutil.rmtree(track_dir + '/fishdata')
        os.makedirs(track_dir + '/fishdata')
        pv_file = track_dir + '/converted.pv'
        launch_tracker = "~/FishTracker/Application/build/tracker -d '" + track_dir + "' -i '" + pv_file + "' -settings fishTracker -nowindow"
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'\t' ,"Running tracker on file: ", track_dir
        try:
            task = subprocess.Popen([launch_tracker],stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True )
            PID = task.pid
            OUT, ERROR = task.communicate()
            if task.returncode != 0:
                if task.returncode == None:
                    task.kill()
                    
                raise Exception('returncode non-zero from tristrack\t' + str(PID) + '\n' + str(task.returncode))
                
            #subprocess.check_call([launch_tracker],stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
        except Exception, e:
            errorLog = open(os.path.expanduser('~/FishTracker/Application/build/batchlog.txt'), 'a')
            errorLog.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t')
            errorLog.write(track_dir + '\t')
            errorLog.write('error during conversion step' + '\n')
            errorLog.write(str(ERROR) + '\n\n\n')
            errorLog.write(str(OUT) + '\n\n\n')
            errorLog.close()
            FNULL.close()
            print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'\t' ,"ERROR tracking file: ", track_dir 
            return
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'\t' ,"Finished tracking on file: ", track_dir 

    FNULL.close()
    
    return


if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--v', type=str, required=True,
                        help='path to video directory')
    parser.add_argument('--make_bkg', type=bool, required=False, default=False,
                        help='make true to generate a new background from this video')
    parser.add_argument('--newonly', type=bool, required=False, default=True,
                        help='make false to save over old data and repeat tracking')
    args = parser.parse_args()
    
    convert(args.v, args.make_bkg, args.newonly)
    track(args.v, args.make_bkg, args.newonly)

