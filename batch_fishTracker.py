import glob
import run_fishTracker
import argparse
import os
from multiprocessing import Process




if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=True,
                        help='path to directory')
    parser.add_argument('--handle', type=str, required=True, 
                        help='provide unique identifier (or comma-separated list) to select a subset of directories.')
    parser.add_argument('--background', type=str, required=False, default=1,
                        help="provide an path or integer descrbing how to handle backgrounds.  path:'\t'Generate a background image from the given directory and use it repeatedly. '\n'0:'\t'use pre-existing.'\n'1:'\t'create one, then use it repeatedly.'\n'>1:'\t'create a new bkg for every video.")
    parser.add_argument('--newonly', type=bool, required=False, default=True,
                        help='make false to retrack and save over old data')
                
    args = parser.parse_args()
    
    HANDLE = args.handle.split(',')
    
    BKG_RULE = args.background
    
    DIR = args.dir
    if DIR[-1] != '/':
        DIR += '/'
    
    if os.path.exists(BKG_RULE):
        import utilities
        utilities.createBackgroundImage(BKG_RULE, method='mean') #FIXME when tristan updates
        mkBkg=False
    elif BKG_RULE == '0':
        mkBkg = False
    else:
        mkBkg = True
    
    
    
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

    
    
    
    
    
    
    


            
            
