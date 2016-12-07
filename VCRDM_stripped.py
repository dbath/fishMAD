#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy2 Experiment Builder (v1.84.2),
    on Wed Nov 23 09:29:35 2016
If you publish work using this script please cite the PsychoPy publications:
    Peirce, JW (2007) PsychoPy - Psychophysics software in Python.
        Journal of Neuroscience Methods, 162(1-2), 8-13.
    Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy.
        Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008
"""

from __future__ import absolute_import, division
from psychopy import gui, visual, core, data, event, logging, sound #locale_setup,
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions
import sys  # to get file system encoding

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

# Store info about the experiment session
expName = u'untitled'  # from the Builder filename that created this script
expInfo = {'participant':'', 'session':'001'}
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = _thisDir + os.sep + u'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath=None,
    savePickle=True, saveWideText=True,
    dataFileName=filename)
# save a log file for detail verbose info
#logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

endExpNow = False  # flag for 'escape' or other condition => quit the exp

# Start Code - component code to be run before the window creation

# Setup the Window
win = visual.Window(
    size=(1440, 900), fullscr=True, screen=0,
    allowGUI=False, allowStencil=False,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
    blendMode='avg')
# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
    print "FOUND THE FRAMERATE!!!!!!!!!!!!!!!!"
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess
print frameDur, round(expInfo['frameRate'])
win.monitorFramePeriod = frameDur


# Create some handy timers
#globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine


def runBlock(_image, _dots, _duration):
    # ------Prepare to start Routine "rest"-------
    t = 0
    myClock = core.Clock()
    myClock.reset()  # clock
    continueRoutine = True
    global routineTimer
    routineTimer.add(_duration)
    # update component parameters for each repeat
    # keep track of which components have finished
    myComponents = [_image, _dots]
    for thisComponent in myComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    _dots.setAutoDraw('foo')   
    # -------Start Routine "rest"-------
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = myClock.getTime()
            
        # *dots_2* updates
        if t >= 0.0 and _dots.status == NOT_STARTED:
            _image.setAutoDraw(True)
            _dots.setAutoDraw(True)
        frameRemains = 0.0 + _duration - win.monitorFramePeriod * 0.75  # most of one frame period left
        if _dots.status == STARTED and t >= frameRemains:
            _dots.setAutoDraw(False)
            _image.setAutoDraw(False)
            
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in myComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
            
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
            
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
        
    # -------Ending Routine "my"-------
    for thisComponent in myComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    return

def setStim(_nDots, _dotSize, _speed, _dir, _co):
    dots = visual.DotStim(
        win=win, name='dots',
        nDots=_nDots, dotSize=_dotSize,
        speed=_speed, dir=_dir, coherence=_co,
        fieldPos=(0.0, 0.0), fieldSize=4,fieldShape='square',
        signalDots='different', noiseDots='direction',dotLife=1000,
        color=[-1.0,-1.0,-1.0], colorSpace='rgb', opacity=1,
        depth=-1.0)
    return dots


# Initialize components for Routine "TEST"
image = visual.ImageStim(
    win=win, name='image',
    image=None, mask=None,
    ori=0, pos=(0, 0), size=(2, 2),
    color=[1.0,1.00,1.000], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)

dots = visual.DotStim(
    win=win, name='dots',
    nDots=400, dotSize=20,
    speed=0.05, dir=0.0, coherence=1.0,
    fieldPos=(0.0, 0.0), fieldSize=4,fieldShape='square',
    signalDots='different', noiseDots='direction',dotLife=1000,
    color=[-1.0,-1.0,-1.0], colorSpace='rgb', opacity=1,
    depth=-1.0)

print "Here goes nothing"
rest = setStim(400, 20, 0, 0, 1)
stim1 = setStim(400, 20, 0.0125, 0, 1)
stim2 = setStim(400, 20, 0.0625, 180, 1)
stim3 = setStim(400, 20, 0.0625, 245, 0.8)
runBlock(image, rest, 3)
runBlock(image, stim1, 10)
runBlock(image, stim2, 10)
runBlock(image, stim3, 10)
runBlock(image, rest, 10)
stim2.speed = 0.25
stim2.coherence=0.6
runBlock(image, stim2,10)
runBlock(image, rest, 10)

print "**********************************finished!"

# these shouldn't be strictly necessary (should auto-save)
#thisExp.saveAsWideText(filename+'.csv')
#thisExp.saveAsPickle(filename)
logging.flush()
# make sure everything is closed down
thisExp.abort()  # or data files will save again on exit
win.close()
core.quit()
