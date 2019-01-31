
from utilities import *
import utilities

import os
import argparse


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



class Mover(object):

    def __init__(self, rigID, sourcefile, destdir):
        self.ANDROID_IP = rigID
        self.SOURCE = sourcefile
        self.DEST = slashdir(destdir)
        self.BASE_DIRECTORY = 'media/recnodes/dotbot_logs/'
        self.FN = getTimeStringFromTime() + '_' + self.SOURCE.split('/')[-1]
        self.destfile = self.BASE_DIRECTORY + self.DEST + self.FN
        self.MULTICAM = False
        
    def move(self):
        if not os.path.exists(self.BASE_DIRECTORY + self.DEST):
            os.makedirs(self.BASE_DIRECTORY + self.DEST)  
        if self.MULTICAM:
            utilities.copyWindowsLog('/media/recnodes/Dan_storage/dotbot_temp_logs/dotbot_log_temp.txt', self.destfile)             
        else:
            utilities.copyAndroidLog(self.ANDROID_IP, self.SOURCE, self.destfile)
        print "copied: ", self.destfile
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--rigs', type=str, required=True,
                        help="IP addresses of Android rigs to record on: example '10.126.18.114,10.126.18.115'")
    parser.add_argument('--source', type=str, required=True,
                        help="full path of file to be copied, can be list in same order as rigs. example: 'fwdbackmix_32_dotbot,fwdbackmix_128_dotbot'")  
    parser.add_argument('--dest', type=str, required=True,
                        help="name of dest directory, can a be list in same order as rigs. example: 'fwdbackmix_32_dotbot,fwdbackmix_128_dotbot'\nFiles will be copied to /recnodes/dotbot_logs/<this directory>") 
                        
    args = parser.parse_args()
                        
    RIG_IDs = args.rigs.split(',')
    SOURCES = args.source.split(',')
    DESTS = args.dest.split(',')
    
    print RIG_IDs
    print SOURCES
    print DESTS
                        
    if len(SOURCES) == 1:     #same expID across all rigs
        for _ in range(len(RIG_IDs) - 1):
            SOURCES.append(SOURCES[0])  
    elif len(SOURCES) != len(RIG_IDs):
        print "ERROR: sources list must match length of rigs" 
        
    if len(DESTS) == 1:     #same expID across all rigs
        for _ in range(len(RIG_IDs) - 1):
            DESTS.append(DESTS[0])  
    elif len(DESTS) != len(RIG_IDs):
        print "ERROR: destinations list must match length of rigs"    
        
        
    
    for item in range(len(RIG_IDs)):
        M = Mover(RIG_IDs[item], SOURCES[item], DESTS[item])
        M.move()
                                          
 
