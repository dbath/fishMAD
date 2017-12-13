import pandas as pd
import utilities
from motifapi import MotifApi as Motif
import time
import os
import datetime
import argparse
from pytz import utc
import logging

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
                    'unknown',
                    '028aa0df3c59b7e364ec931e584e51d1',
                    'ec80e72dbe4fd0641436f7de584e601b',
                    'c883634262cb732016235664584e7665',
                    'c883634262cb732016235664584e7665',
                    '18a6d53607255225ffbc1bae584e6e21',
                    '18a6d53607255225ffbc1bae584e6e21'],

            "IP": [ '10.126.18.38',
                    'bigTank',
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
    def __init__(self, rigID, metadata, FN, DURATION, recstarts, logmovetimes):
        self.ANDROID_IP = rigID
        self.CAMERA_IP = camInfo['IP'][camInfo['rigID'].index(rigID)]
        self.CAMERA_KEY = camInfo['Key'][camInfo['rigID'].index(rigID)]
        self.CAMERA_SERIAL = camInfo['Serial'][camInfo['rigID'].index(rigID)]
        self._metadata = metadata
        self._FN = FN
        self._DURATION = DURATION
        self.BASE_DIRECTORY = '/media/recnodes/recnode_jolle2/'
        self.destfile = self.BASE_DIRECTORY + 'dotbot_logs/dotbotLog_archive_' + rigID[-3:] +'_'+ utilities.getTimeStringFromTime() + '.txt'
        self.api = self.setupAPI()
    
    def setupAPI(self):
        self._codec='nvenc-mq'
        api = Motif(self.CAMERA_IP, self.CAMERA_KEY)
        
        camInfo = pd.DataFrame(api.call('cameras').items()[0][1])
        camName = camInfo[camInfo.serial == self.CAMERA_SERIAL]['name'].values[0]
        if "Ximea" in camName:
            self.CAMERA_SERIAL = camName.split('(')[1][0]
        

        return api   
          
    def configure_camera(self):
        if not (self.api.call('camera/'+self.CAMERA_SERIAL)['camera_info']['status'] == 'ready'):
            raise Exception('CAMERA IS ALREADY IN USE')
        #camsn = api.call('cameras')['cameras'][0]['serial']
        self.api.call('camera/' + self.CAMERA_SERIAL + '/configure', 
                AcquisitionFrameRate=40.0,
                ExposureTime=2000.0 )
        return
        
    def loopbio_record(self, FN, DUR, META):
        
        if not (self.api.call('camera/'+self.CAMERA_SERIAL)['camera_info']['status'] == 'ready'):
            raise Exception('CAMERA IS ALREADY IN USE')
            
        foo = self.api.call('camera/' + self.CAMERA_SERIAL + '/recording/start',
                duration=DUR,
                filename=FN,
                codec=self._codec,
                record_to_store=True, 
                metadata=META)
        return foo          
        
    def copyData(self):
        self.api.call('recordings/copy_all')
        return
        
    def record(self):
        self.configure_camera()
        self.vidfile = self.loopbio_record( self._FN, self._DURATION, self._metadata)
        print "initiated recording: ", self.ANDROID_IP, self.vidfile['filename'].split('/')[0]
        self.destfile = self.BASE_DIRECTORY + 'dotbot_logs/dotbotLog_' + self.vidfile['filename'].split('/')[0] + '.txt'
        return 
          
    def movelog(self):
        if not os.path.exists(self.BASE_DIRECTORY + 'dotbot_logs'):
            os.makedirs(self.BASE_DIRECTORY + 'dotbot_logs')               
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
    parser.add_argument('--session_duration', type=int, required=False, default=3,
                        help='length of video in hours')
    args = parser.parse_args()

    logging.basicConfig()

    recordings = BackgroundScheduler() #schedule recordings
    logfilecopies = BackgroundScheduler()  #schedule copying of log files to server with matching timestamp in FN


    RIG_IDs = args.rigs.split(',')
    expIDs = args.expID.split(',')

    if len(expIDs) == 1:     #same expID across all rigs
        for _ in range(len(RIG_IDs) - 1):
            expIDs.append(expIDs[0])    
    elif len(expIDs) != len(RIG_IDs):
        print "ERROR: expIDs list must match length of rigs"
        
    
    print expIDs

    for item in range(len(RIG_IDs)):
        meta={'expID':args.expID, 'Rig': RIG_IDs[item]}
        SCHEDULE_OFFSET = int(RIG_IDs[item][-2:])    #returns a unique number between 11 and 18 based on IP
        recstarts = ','.join([str(SCHEDULE_OFFSET),str(SCHEDULE_OFFSET + 20),str(SCHEDULE_OFFSET + 40)])
        logmovetimes = ','.join([str(SCHEDULE_OFFSET+12),str(SCHEDULE_OFFSET + 32),str(SCHEDULE_OFFSET -8)])
        E = Experiment(RIG_IDs[item], meta, expIDs[item], args.video_duration, recstarts, logmovetimes)
        
        job_def = {}
        job_def["func"] = E.record
        job_def["trigger"] = 'cron'
        job_def["minute"] = recstarts
        job_def["second"] = 0
        job_def["start_date"] = utilities.getTimeFromTimeString(args.starttime)
        job_def["end_date"] = datetime.datetime.now() + datetime.timedelta(hours=args.session_duration)
        
        _ = recordings.add_job(**job_def)
        job_def = {}
        job_def["func"] = E.movelog
        job_def["trigger"] = 'cron'
        job_def["minute"] = logmovetimes
        job_def["second"] = 20
        job_def["start_date"] = utilities.getTimeFromTimeString(args.starttime)
        job_def["end_date"] = datetime.datetime.now() + datetime.timedelta(hours=args.session_duration)

        _ = logfilecopies.add_job(**job_def)  


        E.movelog()

        
        print "Scheduling completed: ", RIG_IDs[item]   

    print "Starting scheduled events:"
    recordings.start()
    logfilecopies.start()
    for x in recordings.get_jobs():
        print x
    for x in logfilecopies.get_jobs():
        print x

        
    time.sleep((args.session_duration + 0.3)*3600.0)
    
