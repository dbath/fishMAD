
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
            
            
            
for handle in HANDLES:
    for directory in DIRECTORIES:
        for fn in glob.glob('/media/recnodes/' + directory + '/*' + handle + '*/track/vsTime_dRotation_cRotation_stateDepRotOrder.png'):
            print fn
            newfn = '/media/recnodes/Dan_storage/180220_sDRO/' + fn.split('/')[4] + '.png'
            shutil.copyfile(fn, newfn)
            
                        
for handle in HANDLES:
    for directory in DIRECTORIES:
        for fn in glob.glob('/media/recnodes/' + directory + '/*' + handle + '*/track/vsTime_dRotation_cRotation_stateDepRotOrder.png'):
            print fn
            newfn = '/media/recnodes/Dan_storage/180220_christina_rotation/PNG/dRotation_cRotation/' + fn.split('/')[4] + '.png'
            shutil.copyfile(fn, newfn)

for handle in HANDLES:
    for directory in DIRECTORIES:
        for fn in glob.glob('/media/recnodes/' + directory + '/*' + handle + '*/track/vsTime_dRotation_cRotation_stateDepRotOrder.svg'):
            print fn
            newfn = '/media/recnodes/Dan_storage/180220_christina_rotation/SVG/dRotation_cRotation/' + fn.split('/')[4] + '.svg'
            shutil.copyfile(fn, newfn)            
            
for handle in HANDLES:
    for directory in DIRECTORIES:
        for fn in glob.glob('/media/recnodes/' + directory + '/*' + handle + '*/track/vsTime_dRotation_polarization.svg'):
            print fn
            newfn = '/media/recnodes/Dan_storage/180220_christina_rotation/SVG/dRotation_polarization/' + fn.split('/')[4] + '.svg'
            shutil.copyfile(fn, newfn)
            
for handle in HANDLES:
    for directory in DIRECTORIES:
        for fn in glob.glob('/media/recnodes/' + directory + '/*' + handle + '*/track/vsTime_dRotation_polarization.png'):
            print fn
            newfn = '/media/recnodes/Dan_storage/180220_christina_rotation/PNG/dRotation_polarization/' + fn.split('/')[4] + '.png'
            shutil.copyfile(fn, newfn)            
            
            
            
expIDs = []
values = []
for filename in glob.glob('/media/recnodes/kn-crec0*/*speedvar_*/track/frame_means_rotation_polarization.pickle'):
    try:
        expID = filename.split('/')[4]
        print filename
        data = get_state_proportions(filename, 0.65, 0.3)
        values.append(data.values)
        expIDs.append(expID)
    except:
        print "_________ERROR!!!"
df = pd.DataFrame(values, columns=['milling','polarized','swarm','unknown'])
df['expIDs'] = expIDs #add the experiment IDs as a column

df.to_csv('/path/to/where/to/save/file.csv', sep=',')
            
            
            
            
            
            
            
            
            
            
