import sys
import time
import os
import pygame
import numpy as np

pygame.init()
DisplayWidth, DisplayHeight = 1240,850
screen = pygame.display.set_mode((DisplayWidth, DisplayHeight), pygame.FULLSCREEN)

VERTICAL_BARS = os.path.join(os.path.dirname(__file__), 'vertical_bars.png')
HORIZONTAL_BARS = os.path.join(os.path.dirname(__file__), 'horizontal_bars.png')
BLANK = os.path.join(os.path.dirname(__file__), 'blank.png')
CURVES = os.path.join(os.path.dirname(__file__), 'curves.png')
DIAGONAL = os.path.join(os.path.dirname(__file__), 'diagonal.png')
DIAGONAL2 = os.path.join(os.path.dirname(__file__), 'diagonal2.png')
BLACKSTARS = os.path.join(os.path.dirname(__file__), 'stars_black.png')
WHITESTARS = os.path.join(os.path.dirname(__file__), 'stars_white.png')





def run_stimulus(_pygame, IMAGE, DIRECTION, SPEED, DURATION, COLOUR):
    
    stim = _pygame.image.load(IMAGE)
    stim = _pygame.transform.scale(stim, (DisplayWidth, DisplayHeight))
    [xdirection, ydirection] = np.sign(SPEED)
    stimBoundary = stim.get_rect()
    w, h = stim.get_size()
    def reset_image():
        x1 = w*xdirection*-1
        y1 = h*ydirection*-1
        x,y = 0,0
        return x,y,x1,y1


    x1 = w*xdirection*-1
    y1 = h*ydirection*-1
    x,y = 0,0
    global running
    start_time = time.time()
    while ((time.time() - start_time) < DURATION) & running:

        for event in _pygame.event.get():
            if event.type == _pygame.QUIT:
                print 'QUITTING!!'
                running = False
                _running = False
                sys.exit()
        
        keyState = _pygame.key.get_pressed()
        if keyState[_pygame.K_ESCAPE]:
            print('\n Closing...')
            running = False
            _pygame.event.pump()        

        x1 = x1 + SPEED[0]
        x = x + SPEED[0]
        y1 = y1 + SPEED[1]
        y = y + SPEED[1]
        if abs(x) > w or abs(y) > h:
            x,y,x1,y1 = reset_image()
        screen.fill(COLOUR)
        screen.blit(stim, (x,y))
        screen.blit(stim, (x1,y1))

        _pygame.display.flip()
        _pygame.display.update()


running = True
while running:
    run_stimulus(pygame, HORIZONTAL_BARS, 'vertical', [0,-10], 5, (255,255,255))
    run_stimulus(pygame, BLANK, 'vertical', [0,-10], 5, (50,50,50))
    run_stimulus(pygame, VERTICAL_BARS, 'horizontal', [2,0], 5, (255,255,255))
    run_stimulus(pygame, VERTICAL_BARS, 'horizontal', [-2,0], 5, (200,200,0))
    run_stimulus(pygame, BLACKSTARS, 'vertical', [0,14], 15, (255,255,30))
    run_stimulus(pygame, WHITESTARS, 'horizontal', [2,0], 15, (20,20,20))
    run_stimulus(pygame, DIAGONAL, 'vertical', [0,23], 15, (0,100,120))
    run_stimulus(pygame, DIAGONAL2, 'vertical', [0,44], 15, (150,20,20))


    pygame.quit()
