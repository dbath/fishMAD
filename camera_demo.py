from __future__ import absolute_import, print_function, division

import pypylon
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import tqdm
import numpy as np
import subprocess as sp

print('Build against pylon library version:', pypylon.pylon_version.version)

available_cameras = pypylon.factory.find_devices()
print('Available cameras are', available_cameras)

# Grep the first one and create a camera for it
cam = pypylon.factory.create_device(available_cameras[-1])

# We can still get information of the camera back
#print('Camera info of camera object:', cam.device_info)

# Open camera and grep some images
cam.open()

# Hard code exposure time
cam.properties['ExposureTime'] = 1000.0
cam.properties['PixelFormat'] = 'Mono12'
cam.properties['AcquisitionFrameRateEnable'] = True
cam.properties['AcquisitionFrameRate'] = 30 #FPS
#print (list(cam.properties.keys()))
#print(cam.properties['FileSize'])

"""
# Go to full available speed
# cam.properties['DeviceLinkThroughputLimitMode'] = 'Off'

for key in cam.properties.keys():
    try:
        value = cam.properties[key]
    except IOError:
        value = '<NOT READABLE>'

    print('{0} ({1}):\t{2}'.format(key, cam.properties.get_description(key), value))

counter = 0
while True:
    cam.grab_image()
    vid = cam.grab_images(200)


    for image in vid:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.imshow(image, cmap = cm.Greys_r)
        plt.setp(ax.get_yticklabels(), visible=False)
        plt.setp(ax.get_xticklabels(), visible=False)
        plt.subplots_adjust(left=0.0, bottom=0.0, right=1.00, top=1.00, wspace=0, hspace=0)
        plt.savefig('/Users/bathd/Desktop/test2/vid' + str(counter) + '.png', bbox_inches='tight', pad_inches=0)
        plt.close('all')
        counter +=1

    for image in tqdm.tqdm(cam.grab_images(200), leave=True):
        pass

    plt.figure()
    plt.imshow(np.mean([img for img in cam.grab_images(100)], axis=0, dtype=np.float))
    plt.show()

"""


counter = 0


plt.figure()
counter=0
for image in cam.grab_images(1000):
    np.save('/Users/bathd/Desktop/test2/trial%06d.npy'%(counter), image)
    counter +=1

"""
#fig = plt.figure()
for image in cam.grab_images(100):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.imshow(image, cmap = cm.Greys_r)
    plt.setp(ax.get_yticklabels(), visible=False)
    plt.setp(ax.get_xticklabels(), visible=False)
    plt.subplots_adjust(left=0.0, bottom=0.0, right=1.00, top=1.00, wspace=0, hspace=0)
    plt.savefig('/Users/bathd/Desktop/test2/desk' + str(counter) + '.png', bbox_inches='tight', pad_inches=0)
    plt.close('all')
    counter +=1



FFMPEG_BIN = "ffmpeg"

# read 2048*2048*1 bytes (= 1 frame)
raw_image = pipe.stdout.read(2048*2048*1)
# transform the byte read into a numpy array
image =  numpy.fromstring(raw_image, dtype='uint8')
image = image.reshape((2048,2048,1))
# throw away the data in the pipe's buffer.
pipe.stdout.flush()


command = [ FFMPEG_BIN,
        '-y', # (optional) overwrite output file if it exists
        '-f', 'rawvideo',
        '-vcodec','rawvideo',
        '-s', '2048x2048', # size of one frame
        '-pix_fmt', 'mono12',
        '-r', '30', # frames per second
        '-i', '-', # The imput comes from a pipe
        '-an', # Tells FFMPEG not to expect any audio
        '-vcodec', 'mpeg',
        '/Users/bathd/Desktop/test2/desk.mp4' ]

pipe = sp.Popen( command, stdin=sp.PIPE, stderr=sp.PIPE)

pipe.proc.stdin.write( image_array.tostring() )



    print(image.shape)
    plt.imshow(image)
    plt.show()
"""
