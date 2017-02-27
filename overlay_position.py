
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import argparse
import os

def annotate_image(img, position):
    ###foo = img[:,:,0] #take only one channel
    
    cv2.circle(img, (position[0],position[1]),4,(0,0,255),-1)
    
    return img




if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input', type=str, required=True,
                        help='path to original video')
    parser.add_argument('--data', type=str, required=True, help='path to tracking data')
    parser.add_argument('--output', type=str, required=True,
                        help='path to save annotated video')
    parser.add_argument('--make_movie', type=int, required=False, default=0,
                        help='make 1 to generate an annotated movie')
    args = parser.parse_args()
    
    # CONVERT POSITION DATA TO PIXELS
    data = pd.read_csv(args.data, sep=',')
    #data['x'] = (data['X (cm)']*97.7) + 977.0
    #data['y'] = (data['Y (cm)']*97.7) + 1024.0
    data['y'] = (data['Y (cm)']*10.24) + 1024.0
    data.loc[data['x'] == np.nan, 'x'] = 0
    data.loc[data['y'] == np.nan, 'y'] = 0
    data['x'].fillna(0)
    data['y'].fillna(0)
    
    
    #open video and get specs
    video = cv2.VideoCapture(args.input)
    FPS = video.get(5)
    framecount = video.get(7)
    videoformat = video.get(6)
    videoSize = (int(video.get(3)), int(video.get(4)))
    print 'Video is in ', videoformat, 'with', framecount, 'frames at ', FPS, 'fps.'

    counter = 0
    
    #set starting frame
    video.set(1, counter)
    print "STARTING AT FRAME", counter

    if args.make_movie:
        out = cv2.VideoWriter(args.output,cv2.cv.FOURCC('a','v','c','1'), FPS, videoSize)

    while video.isOpened():
        ret, _img = video.read()
        if ret == True:
            if counter < len(data):
                if args.make_movie:
                    position = (data.loc[counter, 'x'].astype(int), data.loc[counter,'y'].astype(int))
                    image = annotate_image(_img, position)
                    out.write(image)

                counter += 1
            else:
                video.release()
                break
        else:
            break

    video.release()

    if args.make_movie == 1:
        out.release()


