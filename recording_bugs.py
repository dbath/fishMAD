import pandas as pd
import numpy as np
from utilities import getTimeFromTimeString
from utilities import copyAndroidLog
from utilities import getTimeStringFromTime
import utilities
from motifapi import MotifApi as Motif
import time
import os
import datetime
import argparse
from pytz import utc
import logging
import apscheduler
import datetime
#import pause
from apscheduler.schedulers.background import BackgroundScheduler


camInfo = {"rigID":['10.126.18.111',
                    '10.126.18.112',
                    '10.126.18.113',
                    '10.126.18.114',
                    '10.126.18.115',
                    '10.126.18.116',
                    '10.126.18.117',
                    '10.126.18.118'], 

            "Key": ['028aa0df3c59b7e364ec931e584e51d1',
                    'b4ea527a5e049f6770c2405158666136',
                    '028aa0df3c59b7e364ec931e584e51d1',
                    'ec80e72dbe4fd0641436f7de584e601b',
                    'c883634262cb732016235664584e7665',
                    'c883634262cb732016235664584e7665',
                    '18a6d53607255225ffbc1bae584e6e21',
                    '18a6d53607255225ffbc1bae584e6e21'],

            "IP": [ '10.126.18.38',
                    '10.126.18.49',
                    '10.126.18.38',
                    '10.126.18.35',
                    '10.126.18.36',
                    '10.126.18.36',
                    '10.126.18.37',
                    '10.126.18.37'],
                    
            "Serial": [ 'unknown',
                        'unknownsetof4',
                        'unknown',
                        '1D000018DCBF8901',
                        '21990453',
                        '21990448',
                        'C8000018F056CC01',
                        'C1000018EFCFEF01']}


    
    
class Experiment(object):
    def __init__(self, rigID, metadata, FN, DURATION, FRAMERATE):
        self.ANDROID_IP = rigID
        self.CAMERA_IP = camInfo['IP'][camInfo['rigID'].index(rigID)]
        self.CAMERA_KEY = camInfo['Key'][camInfo['rigID'].index(rigID)]
        self.CAMERA_SERIAL = camInfo['Serial'][camInfo['rigID'].index(rigID)]
        self._metadata = metadata
        self._FN = FN
        self._DURATION = DURATION
        self.BASE_DIRECTORY = '/media/recnodes/recnode_jolle2/'
        self.destfile = self.BASE_DIRECTORY + 'dotbot_logs/dotbotLog_archive_' + rigID[-3:] +'_'+ getTimeStringFromTime() + '.txt'
        self.framerate=FRAMERATE
        self.api = self.setupAPI()
    
    def setupAPI(self):
        self._codec='mq'
        api = Motif(self.CAMERA_IP, self.CAMERA_KEY)
        
        caminfo = pd.DataFrame(api.call('cameras').items()[0][1])
        if len(caminfo) >1:
            self.MULTICAM = True
        else:
            self.MULTICAM = False            
        serials = []
        print caminfo
        for cam in caminfo.index:
            if "Ximea" in caminfo.ix[cam]['name']:
                serials.append(cam['name'].split('(')[1][0])
            else:
                serials.append(caminfo.ix[cam]['serial'])
        self.CAMERA_SERIAL = serials                

        return api   
          
    def configure_camera(self):
        
        for cam in self.CAMERA_SERIAL:
            if not (self.api.call('camera/'+cam)['camera_info']['status'] == 'ready'):
                raise Exception('CAMERA IS ALREADY IN USE')
            #camsn = api.call('cameras')['cameras'][0]['serial']
            self.api.call('camera/' + cam + '/configure', 
                    AcquisitionFrameRate=self.framerate,
                    ExposureTime=1000.0 )               

        return
        
    def loopbio_record(self, FN, DUR, META):
        for cam in self.CAMERA_SERIAL:
            if not (self.api.call('camera/'+cam)['camera_info']['status'] == 'ready'):
                raise Exception('CAMERA IS ALREADY IN USE')
        if self.MULTICAM:
            cameraCall = 'recording/start'
        else:    
            cameraCall = 'camera/' + self.CAMERA_SERIAL[0] + '/recording/start'
        foo = self.api.call(cameraCall,
                duration=DUR,
                filename=FN,
                codec=self._codec,
                record_to_store=True, 
                metadata=META)
        return foo          
        
    def copyData(self):
        self.api.call('recordings/copy_all', delete_after=True)
        return
        
    def record(self):
        self.configure_camera()
        self.loopbio_record( self._FN, self._DURATION, self._metadata)
        time.sleep(3)
        info = self.api.call('camera/' + self.CAMERA_SERIAL[0])
        self.vidfile = info.items()[1][1]['filename']
        print "initiated recording: ", self.ANDROID_IP, self.vidfile.split('.')[0]
        self.destfile = self.BASE_DIRECTORY + 'dotbot_logs/dotbotLog_' + self.vidfile.split('.')[0] + '.txt'
        return 
          
    def movelog(self):
        if not os.path.exists(self.BASE_DIRECTORY + 'dotbot_logs'):
            os.makedirs(self.BASE_DIRECTORY + 'dotbot_logs')  
        if self.MULTICAM:
            utilities.copyWindowsLog('/media/recnodes/Dan_storage/dotbot_temp_logs/dotbot_log_temp.txt', self.destfile)             
        else:
            utilities.copyAndroidLog(self.ANDROID_IP, '/sdcard/dotbot/dotbot_log.txt', self.destfile)
        print "copied: ", self.destfile
        return



if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--rigs', type=str, required=True,
                        help="IP addresses of Android rigs to record on: example '10.126.18.114,10.126.18.115'")
    parser.add_argument('--expID', type=str, required=True,
                        help="filename identifier, can be list in same order as rigs. example: 'fwdbackmix_32_dotbot,fwdbackmix_128_dotbot'")
    parser.add_argument('--video_duration', type=int, required=False, default=600,
                        help='length of video in seconds')
    parser.add_argument('--starttime', type=str, required=False, default=None,
                        help='start time, in format "HHMMSS" or "YYYYMMDD_HHMMSS" default=Now.')
    parser.add_argument('--number_of_sessions', type=int, required=False, default=12,
                        help='number of repeats, 20min each')
    args = parser.parse_args()


    RIG_IDs = args.rigs.split(',')
    expIDs = args.expID.split(',')



    logging.basicConfig()
    #logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    recordings = BackgroundScheduler() #schedule recordings
    logfilecopies = BackgroundScheduler()  #schedule copying of log files to server with matching timestamp in FN

    end_date = utilities.getTimeFromTimeString(args.starttime) + datetime.timedelta(hours=(args.number_of_sessions + 1))

    if len(expIDs) == 1:     #same expID across all rigs
        for _ in range(len(RIG_IDs) - 1):
            expIDs.append(expIDs[0])    
    elif len(expIDs) != len(RIG_IDs):
        print "ERROR: expIDs list must match length of rigs"
        
    rectimes = [30,25]
    video_durations = [3295,295]
    framerates=[20,90]
    
    print expIDs
    experimentlist = []
    for item in range(len(rectimes)):
        meta={'expID':args.expID, 'Rig': RIG_IDs[0]}
        recstarts = rectimes[item]
        
        #recstarts = ','.join([str(SCHEDULE_OFFSET),str(SCHEDULE_OFFSET + 20),str(SCHEDULE_OFFSET + 40)])
        #logmovetimes = ','.join([str(SCHEDULE_OFFSET+12),str(SCHEDULE_OFFSET + 32),str(SCHEDULE_OFFSET -8)])
        E = Experiment(RIG_IDs[0], meta, expIDs[0], video_durations[item], framerates[item])
        
        job_def = {}
        job_def["func"] = E.record
        job_def["trigger"] = 'cron'
        job_def["minute"] = recstarts
        job_def["second"] = 0
        job_def["start_date"] = utilities.getTimeFromTimeString(args.starttime)
        
        #print "JOBS:", job_def['start_date'], job_def['end_date']        
        _ = recordings.add_job(**job_def)
        if item == -1: #FIXME cancelling data copy for now 190625
            job_def = {}
            job_def["func"] = E.copyData
            job_def["trigger"] = 'cron'
            job_def["minute"] = recstarts
            job_def["second"] = 40
            job_def["start_date"] = utilities.getTimeFromTimeString(args.starttime)
            #job_def["end_date"] = utilities.getTimeFromTimeString(args.starttime) + datetime.timedelta(hours=(args.number_of_sessions +2))
            #print job_def['end_date']
            _ = logfilecopies.add_job(**job_def)  


        E.movelog()
        experimentlist.append(E)
        
        print "Scheduling completed: ", RIG_IDs[0]   

    print "Starting scheduled events:"
    recordings.start()
    logfilecopies.start()
    recordings.print_jobs()
    for x in recordings.get_jobs():
        print x
    for x in logfilecopies.get_jobs():
        print x
    
    time.sleep((args.number_of_sessions + 0.2)*3600.0)
    #pause.until(end_date)
    recordings.shutdown()
    logfilecopies.shutdown()
    for exp in experimentlist:
        exp.movelog()    #make sure the last logs are copied.
    print "Done."

