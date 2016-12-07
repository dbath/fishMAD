import cv2
import pypylon

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
cam.properties['ExposureTime'] = 10000.0
cam.properties['PixelFormat'] = 'Mono12'
cam.properties['AcquisitionFrameRateEnable'] = True
cam.properties['AcquisitionFrameRate'] = 30 #FPS
#print(cam.properties.keys())


FILENAME = '/Users/bathd/Desktop/test2/desk.mp4'



camera = cv2.VideoCapture(0)
video  = cv2.VideoWriter(FILENAME, -1, 25, (2048, 2048));
while True:
   f,img = camera.read()
   video.write(img)
   cv2.imshow("webcam",img)
   if (cv2.waitKey(5) != -1):
       break
video.release()
