
import glob
import shutil

for handle in HANDLES:
    for directory in DIRECTORIES:
        for fn in glob.glob('/media/recnodes/' + directory + '/*' + handle + '*/track/vsTime_dRotation_polarization.png'):
            newfn = '/media/recnodes/Dan_storage/180131_christina/' + fn.split('/')[4] + '.png'
            shutil.copyfile(fn, newfn)
            
            
            

for handle in HANDLES:
    for directory in DIRECTORIES:
        for fn in glob.glob('/media/recnodes/' + directory + '/*' + handle + '*/track/frame_means_rotation_polarization.pickle'):
            
            for x in redo:
                if x in fn:
                    shutil.move(fn, '/media/recnodes/Dan_storage/trash/' + fn.split('/')[4] + '.pickle')




for handle in HANDLES:
    for directory in DIRECTORIES:
        for fn in glob.glob('/media/recnodes/' + directory + '/*' + handle + '*/track/NNstatistics.svg'):
            newfn = '/media/recnodes/Dan_storage/180213_nearest_neighbours_christina/' + fn.split('/')[4] + '.svg'
            shutil.copyfile(fn, newfn)
