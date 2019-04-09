#!/usr/bin/python


import imgstore
import os
import numpy as np
import shutil
import subprocess
import argparse
import scipy.misc
import datetime
from utilities import *
import __future__


def replace_background(_main_dir):
    if os.path.exists(_main_dir + 'track/video_average.png'):
        shutil.copy(_main_dir + 'track/video_average.png',
                    os.path.expanduser('~/FishTracker/Application/build/video_average.png'))
        print("retrieved previous background image")
    else:
        
        #create new background image
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '\t' ,"generating background image...")
        import utilities
        bkg = utilities.createBackgroundImage(_main_dir, 'mean')  #FIXME change to mode after tristan fixes
        scipy.misc.imsave(os.path.expanduser('~/FishTracker/Application/build/video_average.png'), bkg)
        scipy.misc.imsave(_main_dir + 'track/video_average.png', bkg)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '\t' ,"got new background...")
    return

def oddSizeBugfix(_main_dir, axis, newsize):
    """
    fixes LoopBio's odd-numbered movie dimension bug
    call with main directory, int (0 or 1) for dimension to correct, and int for corrected size
    """
    f = np.load(_main_dir + '000000.npz')
    keys = [key for key in f.files]
    nf = {}
    for name in keys:
        nf[name] = f[name]
    nf["imgshape"][axis] = newsize
    print("adjusted video shape: ", f["imgshape"], '>', nf["imgshape"])
    np.savez(_main_dir + '000000', **nf)
    return
    
def setup_tristrack(_main_dir, fishnum):
    print("initiating tracking settings for:", _main_dir)
    MAIN_DIR = _main_dir
    if MAIN_DIR[-1] != '/':
        MAIN_DIR += '/'
    track_dir = MAIN_DIR + 'track'
    if not os.path.exists(track_dir):
        os.makedirs(track_dir)
 
    #copy default settings files and make fishdata dir

    if not os.path.exists(track_dir + 'fishTrXXXacker.settings'):
        if 'stitched' in MAIN_DIR:
            shutil.copyfile(os.path.expanduser('~/fishMAD/tristrack_defaults/fishTracker3m.settings'), track_dir + '/fishTracker.settings')
            shutil.copyfile(os.path.expanduser('~/fishMAD/tristrack_defaults/3m_bkg.png'), track_dir + '/average_converted.pv.png')
        else:
            shutil.copyfile(os.path.expanduser('~/fishMAD/tristrack_defaults/fishTracker.settings'), track_dir + '/fishTracker.settings')
    if not os.path.exists(track_dir + 'conversion.settings'):
        if 'stitched' in MAIN_DIR:
            shutil.copyfile(os.path.expanduser('~/fishMAD/tristrack_defaults/conversion3m.settings'), track_dir + '/conversion.settings')
        else:
            shutil.copyfile(os.path.expanduser('~/fishMAD/tristrack_defaults/conversion.settings'), track_dir + '/conversion.settings')
    if not os.path.exists(track_dir + '/fishdata'):
        os.makedirs(track_dir + '/fishdata')


    #Get metadata from videos
    store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml' )
    
    if len(store.user_metadata) >0:
        FPS = store.user_metadata['acquisitionframerate']
    else:
        FPS = 40
        
    #FIX VIDEO SIZE BUG:
    videoSize =store.image_shape
    vidDims = []
    for i in range(len(videoSize)):
        if i == 2:
            j = videoSize[i]
        elif videoSize[i]%2 != 0:
            j = videoSize[i] - 1
            oddSizeBugfix(MAIN_DIR, i, j)
        else:
            j = videoSize[i]
            
        vidDims.append(j)
    videoSize = vidDims


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
        fishnum = int(1.1*fishnum)

    #  customize conversion.settings
    openFile = open(track_dir + '/conversion.settings', 'r')
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
    
    openFile = open(track_dir + '/conversion.settings', 'w')
    openFile.seek(0)
    # clear file content 
    openFile.truncate()
    # re-write the content with the updated content
    openFile.write(''.join(SETTINGS))
    openFile.close()

    print("wrote new conversion file...")
    # Customize fishTracker.settings

    #   get and read tracker settings
    openFile = open(track_dir + '/fishTracker.settings', 'r')
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
    openFile = open(track_dir + '/fishTracker.settings', 'w')
    openFile.seek(0)
    # clear file content 
    openFile.truncate()
    # re-write the content with the updated content
    openFile.write(''.join(SETTINGS))
    openFile.close()

    print("wrote new settings file...")
    
    
    return



def convert(_main_dir, _make_bkg, NEW_ONLY, fishnum, DEBUG):
    MAIN_DIR = _main_dir
    if MAIN_DIR[-1] != '/':
        MAIN_DIR += '/'
    track_dir = MAIN_DIR + 'track'
    if not os.path.exists(track_dir):
        os.makedirs(track_dir)
    store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml')
    nFrames = store.frame_count
    
    if (NEW_ONLY) and (os.path.exists(track_dir + 'converted.results')):
        return
    
    if _make_bkg == True:
        replace_background(MAIN_DIR)

    FNULL = open(os.devnull, 'w')

    # Launch conversion
    vidSet = MAIN_DIR + '%6d.mp4'
    launch_conversion = "~/FishTracker/Application/build/framegrabber -d '" + track_dir + "' -i '" + vidSet + "' -o converted.pv -settings '" + track_dir + "/conversion.settings'"
    if DEBUG==False:
        launch_conversion += " -nowindow"
    if not (os.path.exists(track_dir + '/converted.pv')):
        #if os.path.exists(os.path.expanduser('~/FishTracker/Application/build/video_average.png')):
        #    os.remove(os.path.expanduser('~/FishTracker/Application/build/video_average.png'))
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '\t' ,"Running conversion on file: ", track_dir)
        #try:
        print(launch_conversion)
        try:
            task = subprocess.Popen([launch_conversion],stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)#FNULL
            PID = task.pid
            print('Process ID: ', PID)
            while task.stdout is not None:
                try:
                    line = task.stdout.readline().decode()
                    sp = line.split(' ')
                    if (len(sp) == 11) and (sp[3] == 'FPS:'): #read only progress report lines
                        printProgressBar(int(sp[1].split('/')[0]), nFrames, 
                                prefix='Converting: ', 
                                suffix='ETA'+ line.split('eta:')[1].split('),')[0])
                    if not line:
                        print("\n")
                        task.stdout.flush()
                        break
                except:
                    pass
            OUT, ERROR = task.communicate()
            if task.returncode != 0:
                #if task.returncode == None:
                task.kill()
                    
                raise Exception('returncode non-zero from conversion\t' + str(PID) + '\n' + str(task.returncode))
        
        except:# Exception as e:
            errorLog = open(os.path.expanduser('~/FishTracker/Application/build/conversion_log.txt'), 'w')
            errorLog.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t')
            errorLog.write(track_dir + '\t')
            errorLog.write(launch_conversion + '\n')
            errorLog.write('error during conversion step' + '\n')
            errorLog.write(str(ERROR) + '\n')
            errorLog.write('--------------------------------------------------------------------------------------------------------\n\n')
            errorLog.close()
            FNULL.close()
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'\t' ,"ERROR converting file: ", track_dir)
            
        
    FNULL.close()

    return

def track(_main_dir, _make_bkg, NEW_ONLY, fishnum, DEBUG=False):
    setup_tristrack(_main_dir, fishnum)
    MAIN_DIR = slashdir(_main_dir)
    track_dir = MAIN_DIR + 'track'
    # Launch tracker
    FNULL = open(os.devnull, 'w')    
    if 1:#not (os.path.exists(track_dir + '/converted.results')):  #FIXME
        shutil.rmtree(track_dir + '/fishdata')
        os.makedirs(track_dir + '/fishdata')
        pv_file = track_dir + '/converted.pv'
        launch_tracker = "~/FishTracker/Application/build/tracker -d '" + track_dir + "' -i '" + pv_file + "' -settings '" + track_dir + "/fishTracker.settings'"
        if  (os.path.exists(track_dir + '/converted.results')): #FIXME
            launch_tracker += " -load -gui_save_npy_quit true"
        if DEBUG==False:
            launch_tracker += " -nowindow"
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'\t' ,"Running tracker on file: ", track_dir)
        print(launch_tracker)
        store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml')
        nFrames = store.frame_count
        try:
            task = subprocess.Popen([launch_tracker],stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True )#
            PID = task.pid
            print('Process ID: ', PID)
            while task.stdout is not None:
                try:
                    line = task.stdout.readline().decode()
                    if ('frame' in line) and (') filter_blobs' in line)and ('eta ' in line): #read only progress report lines
                        framenum = int(line.split('% frame ')[1].split('/')[0])
                        eta = line.split('eta ')[1].split(')')[0]
                        printProgressBar(framenum, nFrames, prefix='Tracking: ', suffix='ETA: ' + eta)
                    if not line:
                        print("\n")
                        task.stdout.flush()
                        break
                except:
                    pass
            OUT, ERROR = task.communicate()
            if task.returncode != 0:
                #if task.returncode == None:
                task.kill()
                    
                raise Exception('returncode non-zero from tristrack\t' + str(PID) + '\n' + str(task.returncode))
            
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'\t' ,"Finished tracking on file: ", track_dir )
                
            #subprocess.check_call([launch_tracker],stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
        
        except:# Exception(e):
            #print(e)
            errorLog = open(os.path.expanduser('~/FishTracker/Application/build/batchlog.txt'), 'a')
            errorLog.write('--------------------------------------------------------------------------------------------------------\n\n\n')
            errorLog.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n')
            errorLog.write(launch_tracker + '\n')
            errorLog.write('ERROR OUTPUT:' + '\n\n')
            errorLog.write(str(ERROR) + '\n\n\n')
            #errorLog.write(str(OUT) + '\n\n\n')
            errorLog.close()
            FNULL.close()
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'\t' ,"ERROR tracking file: ", track_dir )
        

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
    parser.add_argument('--debug', type=bool, required=False, default=False,
                        help='make true to show window during conversion and tracking')
    args = parser.parse_args()
    
    MAIN_DIR = slashdir(args.v)
    NUM_OF_FISH = int(MAIN_DIR.split('/')[-2].split('_')[1])
    print(NUM_OF_FISH)
    setup_tristrack(args.v, NUM_OF_FISH)
    convert(args.v, args.make_bkg, args.newonly, NUM_OF_FISH)
    track(args.v, args.make_bkg, args.newonly, NUM_OF_FISH)

