import glob
import run_fishTracker
import argparse
import os




if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', type=str, required=True,
                        help='path to directory')
    parser.add_argument('--handle', type=str, required=True, 
                        help='provide a short identifier to select a subset of directories.')
    parser.add_argument('--background', type=str, required=False, default=1,
                        help='provide an integer descrbing how to handle backgrounds.\n0:\tuse pre-existing.\n1:\tcreate one, then use it repeatedly.\n>1:\tcreate a new bkg for every video.')
                
    args = parser.parse_args()
    
    HANDLE = args.handle
    
    BKG_RULE = args.background
    
    DIR = args.dir
    if DIR[-1] != '/':
        DIR += '/'
    
    if '.mp4' in BKG_RULE:
        import utilities
        utilities.createBackgroundImage(DIR, method='mean') #FIXME when tristan updates
        mkBkg=False
    elif BKG_RULE == '0':
        mkBkg = False
    else:
        mkBkg = True
    for vDir in glob.glob(DIR + '*' + HANDLE + '*'):
        if not os.path.exists(vDir + '/track/converted.results'):
            run_fishTracker.doit(vDir, mkBkg)
            if BKG_RULE == '1':
                mkBkg = False
            
            
