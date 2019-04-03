
import imgstore
import os
import numpy as np
import shutil
import subprocess
import argparse
import scipy.misc
import datetime
from utilities import *


def replace_background(_main_dir):
    if os.path.exists(_main_dir + 'track/video_average.png'):
        shutil.copyfile(_main_dir + 'track/video_average.png',
                    os.path.expanduser('~/setup_debian/FishTracker/Application/build/video_average.png'))
        print "retrieved previous background image"
    else:
        
        #create new background image
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '\t' ,"generating background image..."
        import utilities
        bkg = utilities.createBackgroundImage(_main_dir, 'mean')  #FIXME change to mode after tristan fixes
        scipy.misc.imsave(os.path.expanduser('~/setup_debian/FishTracker/Application/build/video_average.png'), bkg)
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
            shutil.copyfile(os.path.expanduser('~/fishMAD/tristrack_defaults/fishTracker_stickleback.settings'), track_dir + '/fishTracker.settings')
        else:
            shutil.copyfile(os.path.expanduser('~/fishMAD/tristrack_defaults/fishTracker.settings'), track_dir + '/fishTracker.settings')
    if not os.path.exists(track_dir + 'conversion.settings'):
        if '_jwj_' in MAIN_DIR:
            shutil.copyfile(os.path.expanduser('~/fishMAD/tristrack_defaults/conversion_stickleback.settings'), track_dir + '/conversion.settings')
        else:
            shutil.copyfile(os.path.expanduser('~/fishMAD/tristrack_defaults/conversion.settings'), track_dir + '/conversion.settings')
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
        fishnum = fishnum*1.1

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
    launch_conversion = "~/setup_debian/FishTracker/Application/build/framegrabber -d '" + track_dir + "' -i '" + vidSet + "' -o converted.pv -settings conversion -nowindow"
    if not (os.path.exists(track_dir + '/converted.pv')):
        if os.path.exists(os.path.expanduser('~/setup_debian/FishTracker/Application/build/video_average.png')):
            os.remove(os.path.expanduser('~/setup_debian/FishTracker/Application/build/video_average.png'))
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '\t' ,"Running conversion on file: ", track_dir
        try:
            subprocess.check_call([launch_conversion],stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
        except Exception, e:
            errorLog = open(os.path.expanduser('~/setup_debian/FishTracker/Application/build/batchlog.txt'), 'w')
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
    
    # GET ALL FILES THAT ARE NOT CONVERTED
    fileList = []
    for term in HANDLE:
        for DIR in DIRECTORIES:
            for vDir in glob.glob(DIR + '*' + term + '*'):
                if (not os.path.exists(vDir + '/track/converted.results')):
                    """
                    try:
                        fishnum = count.count_from_vid(vDir + '000000.mp4')
                    except:
                    """
                    fishnum = int(vDir.split('/')[-1].split('_')[1])
                    print "processing", vDir, str(fishnum)                    
                    convert(vDir, mkBkg, args.newonly, fishnum)



