import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import pandas as pd
import argparse
import os
import imgstore
from subprocess import call
import subprocess
import time

    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--v', type=str, required=True,
                        help='path to video directory')
    parser.add_argument('--IP', type=str, required=True,
                        help='IP address of stimulus generator')
    args = parser.parse_args()
    DIRECTORY = args.v
    if DIRECTORY[-1] != '/':
        DIRECTORY += '/'
    _IP = args.IP

    ipdict = {'111':'10.126.18.111',
              '113':'10.126.18.113',
              '36':'10.126.18.111',
              '35B':'10.126.18.113',
             }

    if '10.126' in _IP:
        IP = _IP
    else:
        IP = ipdict[_IP]


    if not os.path.exists(DIRECTORY + "synchTest_log_from_android.txt"):
        #COPY STIMULUS FILES FROM ANDROID BOX
        
        #call(["cd", "/opt/android-sdk/platform-tools"], shell=True)
        call(["/opt/android-sdk/platform-tools/adb kill-server"], shell=True)
        call(["/opt/android-sdk/platform-tools/adb start-server"], shell=True)
        call(["/opt/android-sdk/platform-tools/adb connect " + IP], shell=True)
        time.sleep(3)
        cmd = "/opt/android-sdk/platform-tools/adb pull -a /sdcard/dan_Data/synchTest_log.txt " + DIRECTORY + 'synchTest_log_from_android.txt'
        call([cmd], shell=True)


    stimData = pd.read_table(DIRECTORY + "synchTest_log_from_android.txt", sep='\t', header=None, names=['Event','Timestamp']).dropna()
    stimData['frame_time'] = stimData['Timestamp']/1000.0

    store = imgstore.new_for_filename(DIRECTORY + 'metadata.yaml' )
    FPS = 30
    videoSize =store.image_shape

    frameDF = pd.DataFrame(store.get_frame_metadata())

    ROI1 = [] #reference
    ROI2 = [] #spot
    for x in range(store.frame_count):
        img, (framenum, frametime) = store.get_next_image()
        ROI2.append(img[ 445:666,1585:1870].mean())
        ROI1.append(img[445:666,1027:1327].mean())
        
    frameDF['ref'] = ROI1
    frameDF['spot'] = ROI2
    frameDF['diff'] = (frameDF['ref'] - frameDF['spot']) / frameDF['ref']
    frameDF['jump'] = frameDF['ref'] - frameDF.shift()['ref']
    merged = frameDF.merge(stimData, how='outer', on='frame_time')
    merged = merged.sort('frame_time').reset_index(drop=True)
    merged.frame_number.fillna(method='ffill', inplace=True)
    merged.spot.fillna(method='ffill', inplace=True)
    merged.ref.fillna(method='ffill', inplace=True)
    blips = merged[merged.Event.notnull()]
    blips.reset_index(drop=True, inplace=True)
    starts = merged.copy()
    starts = starts.sort('jump')
    start = starts[-1:]
    start['Event'] = 'start_detected'
    merged2 = merged.copy()
    spots = merged2[merged2['diff'] > 0.5]
    spots = spots[spots.frame_number - spots.shift().frame_number != 1]
    spots['Event'] = 'spot_detected'
    vblips = pd.concat([start, spots])
    vblips.reset_index(drop=True, inplace=True)
    vblips = vblips[:len(blips)]

    timeOffset = (blips.frame_time - vblips.frame_time).median() #positive when stimclock is ahead
    frameOffset = (blips.frame_number - vblips.frame_number).median() #positive when stimclock is ahead

    img, (f, t) = store.get_image(store.frame_min)
    firstVidTime = pd.to_datetime(t, unit='s').tz_localize('GMT').tz_convert('Europe/Berlin')
    logStart = pd.to_datetime(start['frame_time'].min(), unit='s').tz_localize('GMT').tz_convert('Europe/Berlin')

    print "\n\nVideo started at: ",  firstVidTime
    print "\nSynctest started at: ",  logStart,  '\n\n'


    print "Logged timestamps are ahead of video timestamps by ",  str(timeOffset),  "sec, approx. ",  str(frameOffset) + "frames.\n\n"
    
    if abs(timeOffset) > 0.5:
        print "--------------------------------------------------------------------\n\n\n"
        print " WARNING: stimulus and recording equipment require synchronization.\n\n\n"
        print "--------------------------------------------------------------------\n\n\n"
        
        
    
    blips.to_csv(DIRECTORY + 'syncTest_logEvents.csv')
    vblips.to_csv(DIRECTORY + 'syncTest_detectedEvents.csv')
    timeOffsetDF = (blips.frame_time - vblips.frame_time)
    pd.DataFrame(timeOffsetDF).to_csv(DIRECTORY + 'syncTest_timeOffsets.csv')
