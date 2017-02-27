
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import argparse
import os

def annotate_image(img):
    ###foo = img[:,:,0] #take only one channel
    
    cv2.ellipse(img, (1085,1232),(837,494),-5,-35,35,(255,0,0),4)
    cv2.ellipse(img, (1085,1232),(837,494),-5,35,145,(0,255,0),4)
    cv2.ellipse(img, (1085,1232),(837,494),-5,145,215,(0,0,255),4)
    cv2.ellipse(img, (1085,1232),(837,494),-5,215,325,(255,255,0),4)
    cv2.rectangle(img, (70,70), (1978,452), (255,255,255),4)
    
    return img

def get_regions(img, REGION):
    ###foo = img[:,:,0] #take only one channel
    nulls = np.zeros(img.shape, np.uint8)
    nulls.fill(np.nan)
    if REGION == 'A':
        cv2.ellipse(nulls, (1085,1232),(837,494),-5,-35,35,1,-1)
    if REGION == 'B':
        cv2.ellipse(nulls, (1085,1232),(837,494),-5,35,145,1,-1)
    if REGION == 'C':
        cv2.ellipse(nulls, (1085,1232),(837,494),-5,145,215,1,-1)
    if REGION == 'D':
        cv2.ellipse(nulls, (1085,1232),(837,494),-5,215,325,1,-1)
    if REGION == 'STIM':
        cv2.rectangle(nulls, (70,70), (1978,452), 1,4)
    return nulls

def get_stds(img, regionlist):
    stds = np.zeros(len(regionlist))
    for x in range(len(regionlist)):
        stds[x] = np.nanstd(img*regionlist[x])
    return stds


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input', type=str, required=True,
                        help='path to original video')
    parser.add_argument('--output', type=str, required=True,
                        help='path to save annotated video')
    parser.add_argument('--make_movie', type=int, required=False, default=0,
                        help='make 1 to generate an annotated movie')
    args = parser.parse_args()
    
    #open video and get specs
    video = cv2.VideoCapture(args.input)
    FPS = int(video.get(5))
    framecount = video.get(7)
    videoformat = video.get(6)
    videoSize = (int(video.get(3)), int(video.get(4)))
    print 'Video is in ', videoformat, 'with', framecount, 'frames at ', FPS, 'fps.'
    
    #check for partial data
    if os.path.exists(args.input.rsplit('.',2)[0] + '_data.pickle'):
        data = pd.read_pickle(args.input.rsplit('.',2)[0] + '_data.pickle')
        counter = len(data)-1
        startCounter = counter
    else:
        data = pd.DataFrame(columns=('A','B','C','D','STIM'))
        counter = 0
        startCounter = -1000

    #set starting frame
    video.set(1, counter)
    print "STARTING AT FRAME", counter

    if args.make_movie:
        out = cv2.VideoWriter(args.output,cv2.cv.FOURCC('a','v','c','1'), FPS, videoSize)

    while video.isOpened() and counter<100:
        ret, _img = video.read()
        if ret == True:
            if args.make_movie:
                image = annotate_image(_img)
                out.write(image)
            if (counter == 0) or (counter == startCounter):
                old_img = _img[:,:,0]
                a = get_regions(_img[:,:,0], 'A')
                b = get_regions(_img[:,:,0], 'B')
                c = get_regions(_img[:,:,0], 'C')
                d = get_regions(_img[:,:,0], 'D')
                stim = get_regions(_img[:,:,0], 'STIM')
            diff = _img[:,:,0] - old_img
            stds = get_stds(diff, [a,b,c,d,stim])
            if counter != startCounter:
                data.loc[counter] = stds
            old_img = _img[:,:,0]
            if (counter % 500 == 0) & (counter != startCounter):
                data.to_pickle(args.input.rsplit('.',2)[0] + '_data.pickle')
                print 'Processed ', str(counter), ' frames.'
            counter += 1
        else:
            break

    video.release()

    if args.make_movie == 1:
        out.release()
    data.to_pickle(args.input.rsplit('.',2)[-1] + '_data.pickle')
    s = (data.index.to_series() / 100).astype(int)
    grouped = data.groupby(s).mean().set_index(s.index[0::100])
    grouped.plot(color=['#FF0000','#00FF00','#0000FF','#FFFF00', '#000000'])
    plt.show()

