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

def runBlock(_image, _dots):
    # ------Prepare to start Routine "rest"-------
    t = 0
    myClock = core.Clock()
    myClock.reset()  # clock
    continueRoutine = True
    global routineTimer
    routineTimer.add(60.000000)
    # update component parameters for each repeat
    # keep track of which components have finished
    myComponents = [_image, _dots]
    for thisComponent in myComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
        
    # -------Start Routine "rest"-------
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = myClock.getTime()
            
        # *dots_2* updates
        if t >= 0.0 and _dots.status == NOT_STARTED:
            _image.setAutoDraw(True)
            _dots.setAutoDraw(True)
        frameRemains = 0.0 + 60.0- win.monitorFramePeriod * 0.75  # most of one frame period left
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

# Initialize components for Routine "TEST"
image = visual.ImageStim(
    win=win, name='image',
    image=None, mask=None,
    ori=0, pos=(0, 0), size=(2, 2),
    color=[0.50,0.800,1.000], colorSpace='rgb', opacity=1,
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
runBlock(image, dots)
print "**********************************finished!"
# Initialize components for Routine "rest"
restClock = core.Clock()
image_2 = visual.ImageStim(
    win=win, name='image_2',
    image=None, mask=None,
    ori=0, pos=(0, 0), size=(2, 2),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
dots_2 = visual.DotStim(
    win=win, name='dots_2',
    nDots=400, dotSize=20,
    speed=0, dir=0.0, coherence=1.0,
    fieldPos=(0.0, 0.0), fieldSize=4,fieldShape='circle',
    signalDots='same', noiseDots='direction',dotLife=1000,
    color=[-1.0,-1.0,-1.0], colorSpace='rgb', opacity=1,
    depth=-1.0)

# Initialize components for Routine "routine_1"
routine_1Clock = core.Clock()
image = visual.ImageStim(
    win=win, name='image',
    image=None, mask=None,
    ori=0, pos=(0, 0), size=(2, 2),
    color=[1.000,1.000,1.000], colorSpace='rgb', opacity=1,
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

# Initialize components for Routine "rest"
restClock = core.Clock()
image_2 = visual.ImageStim(
    win=win, name='image_2',
    image=None, mask=None,
    ori=0, pos=(0, 0), size=(2, 2),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
dots_2 = visual.DotStim(
    win=win, name='dots_2',
    nDots=4000, dotSize=20,
    speed=0, dir=0.0, coherence=1.0,
    fieldPos=(0.0, 0.0), fieldSize=4,fieldShape='circle',
    signalDots='same', noiseDots='direction',dotLife=1000,
    color=[-1.0,-1.0,-1.0], colorSpace='rgb', opacity=1,
    depth=-1.0)

# Initialize components for Routine "var_0_7"
var_0_7Clock = core.Clock()
image_3 = visual.ImageStim(
    win=win, name='image_3',
    image=None, mask=None,
    ori=0, pos=(0, 0), size=(2, 2),
    color=[1.000,1.000,1.000], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
dots_3 = visual.DotStim(
    win=win, name='dots_3',
    nDots=4000, dotSize=20,
    speed=0.0005, dir=0.0, coherence=1.0,
    fieldPos=(0.0, 0.0), fieldSize=4,fieldShape='square',
    signalDots='different', noiseDots='direction',dotLife=1000,
    color=[-1.0,-1.0,-1.0], colorSpace='rgb', opacity=1,
    depth=-1.0)

# Initialize components for Routine "rest"
restClock = core.Clock()
image_2 = visual.ImageStim(
    win=win, name='image_2',
    image=None, mask=None,
    ori=0, pos=(0, 0), size=(2, 2),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
dots_2 = visual.DotStim(
    win=win, name='dots_2',
    nDots=4000, dotSize=20,
    speed=0, dir=0.0, coherence=1.0,
    fieldPos=(0.0, 0.0), fieldSize=4,fieldShape='circle',
    signalDots='same', noiseDots='direction',dotLife=1000,
    color=[-1.0,-1.0,-1.0], colorSpace='rgb', opacity=1,
    depth=-1.0)

# Initialize components for Routine "var_0_5"
var_0_5Clock = core.Clock()
image_4 = visual.ImageStim(
    win=win, name='image_4',
    image=None, mask=None,
    ori=0, pos=(0, 0), size=(2, 2),
    color=[1.000,1.000,1.000], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
dots_4 = visual.DotStim(
    win=win, name='dots_4',
    nDots=4000, dotSize=20,
    speed=0.0005, dir=0.0, coherence=1.0,
    fieldPos=(0.0, 0.0), fieldSize=4,fieldShape='square',
    signalDots='different', noiseDots='direction',dotLife=1000,
    color=[-1.0,-1.0,-1.0], colorSpace='rgb', opacity=1,
    depth=-1.0)

# Initialize components for Routine "rest"
restClock = core.Clock()
image_2 = visual.ImageStim(
    win=win, name='image_2',
    image=None, mask=None,
    ori=0, pos=(0, 0), size=(2, 2),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
dots_2 = visual.DotStim(
    win=win, name='dots_2',
    nDots=4000, dotSize=20,
    speed=0, dir=0.0, coherence=1.0,
    fieldPos=(0.0, 0.0), fieldSize=4,fieldShape='circle',
    signalDots='same', noiseDots='direction',dotLife=1000,
    color=[-1.0,-1.0,-1.0], colorSpace='rgb', opacity=1,
    depth=-1.0)

# Initialize components for Routine "var_0"
var_0Clock = core.Clock()
image_5 = visual.ImageStim(
    win=win, name='image_5',
    image=None, mask=None,
    ori=0, pos=(0, 0), size=(2, 2),
    color=[1.000,1.000,1.000], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
dots_5 = visual.DotStim(
    win=win, name='dots_5',
    nDots=4000, dotSize=20,
    speed=0.0005, dir=0.0, coherence=1.0,
    fieldPos=(0.0, 0.0), fieldSize=4,fieldShape='square',
    signalDots='different', noiseDots='direction',dotLife=1000,
    color=[-1.0,-1.0,-1.0], colorSpace='rgb', opacity=1,
    depth=-1.0)

# Initialize components for Routine "rest"
restClock = core.Clock()
image_2 = visual.ImageStim(
    win=win, name='image_2',
    image=None, mask=None,
    ori=0, pos=(0, 0), size=(2, 2),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
dots_2 = visual.DotStim(
    win=win, name='dots_2',
    nDots=4000, dotSize=20,
    speed=0, dir=0.0, coherence=1.0,
    fieldPos=(0.0, 0.0), fieldSize=4,fieldShape='circle',
    signalDots='same', noiseDots='direction',dotLife=1000,
    color=[-1.0,-1.0,-1.0], colorSpace='rgb', opacity=1,
    depth=-1.0)

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine














        
# ------Prepare to start Routine "routine_1"-------
t = 0
routine_1Clock.reset()  # clock
frameN = -1
continueRoutine = True
routineTimer.add(120.000000)
# update component parameters for each repeat
dots.setFieldCoherence(1)
# keep track of which components have finished
routine_1Components = [image, dots]
for thisComponent in routine_1Components:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# -------Start Routine "routine_1"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = routine_1Clock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *image* updates
    if t >= 0.0 and image.status == NOT_STARTED:
        # keep track of start time/frame for later
        image.tStart = t
        image.frameNStart = frameN  # exact frame index
        image.setAutoDraw(True)
    frameRemains = 0.0 + 120.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if image.status == STARTED and t >= frameRemains:
        image.setAutoDraw(False)
    
    # *dots* updates
    if t >= 0.0 and dots.status == NOT_STARTED:
        # keep track of start time/frame for later
        dots.tStart = t
        dots.frameNStart = frameN  # exact frame index
        dots.setAutoDraw(True)
    frameRemains = 0.0 + 120.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if dots.status == STARTED and t >= frameRemains:
        dots.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in routine_1Components:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "routine_1"-------
for thisComponent in routine_1Components:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

# ------Prepare to start Routine "rest"-------
t = 0
restClock.reset()  # clock
frameN = -1
continueRoutine = True
routineTimer.add(60.000000)
# update component parameters for each repeat
# keep track of which components have finished
restComponents = [image_2, dots_2]
for thisComponent in restComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# -------Start Routine "rest"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = restClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *image_2* updates
    if t >= 0.0 and image_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        image_2.tStart = t
        image_2.frameNStart = frameN  # exact frame index
        image_2.setAutoDraw(True)
    frameRemains = 0.0 + 60.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if image_2.status == STARTED and t >= frameRemains:
        image_2.setAutoDraw(False)
    
    # *dots_2* updates
    if t >= 0.0 and dots_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        dots_2.tStart = t
        dots_2.frameNStart = frameN  # exact frame index
        dots_2.setAutoDraw(True)
    frameRemains = 0.0 + 60.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if dots_2.status == STARTED and t >= frameRemains:
        dots_2.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in restComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "rest"-------
for thisComponent in restComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

# ------Prepare to start Routine "var_0_7"-------
t = 0
var_0_7Clock.reset()  # clock
frameN = -1
continueRoutine = True
routineTimer.add(120.000000)
# update component parameters for each repeat
dots_3.setFieldCoherence(0.7)
# keep track of which components have finished
var_0_7Components = [image_3, dots_3]
for thisComponent in var_0_7Components:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# -------Start Routine "var_0_7"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = var_0_7Clock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *image_3* updates
    if t >= 0.0 and image_3.status == NOT_STARTED:
        # keep track of start time/frame for later
        image_3.tStart = t
        image_3.frameNStart = frameN  # exact frame index
        image_3.setAutoDraw(True)
    frameRemains = 0.0 + 120.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if image_3.status == STARTED and t >= frameRemains:
        image_3.setAutoDraw(False)
    
    # *dots_3* updates
    if t >= 0.0 and dots_3.status == NOT_STARTED:
        # keep track of start time/frame for later
        dots_3.tStart = t
        dots_3.frameNStart = frameN  # exact frame index
        dots_3.setAutoDraw(True)
    frameRemains = 0.0 + 120.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if dots_3.status == STARTED and t >= frameRemains:
        dots_3.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in var_0_7Components:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "var_0_7"-------
for thisComponent in var_0_7Components:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

# ------Prepare to start Routine "rest"-------
t = 0
restClock.reset()  # clock
frameN = -1
continueRoutine = True
routineTimer.add(60.000000)
# update component parameters for each repeat
# keep track of which components have finished
restComponents = [image_2, dots_2]
for thisComponent in restComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# -------Start Routine "rest"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = restClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *image_2* updates
    if t >= 0.0 and image_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        image_2.tStart = t
        image_2.frameNStart = frameN  # exact frame index
        image_2.setAutoDraw(True)
    frameRemains = 0.0 + 60.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if image_2.status == STARTED and t >= frameRemains:
        image_2.setAutoDraw(False)
    
    # *dots_2* updates
    if t >= 0.0 and dots_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        dots_2.tStart = t
        dots_2.frameNStart = frameN  # exact frame index
        dots_2.setAutoDraw(True)
    frameRemains = 0.0 + 60.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if dots_2.status == STARTED and t >= frameRemains:
        dots_2.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in restComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "rest"-------
for thisComponent in restComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

# ------Prepare to start Routine "var_0_5"-------
t = 0
var_0_5Clock.reset()  # clock
frameN = -1
continueRoutine = True
routineTimer.add(120.000000)
# update component parameters for each repeat
dots_4.setFieldCoherence(0.5)
# keep track of which components have finished
var_0_5Components = [image_4, dots_4]
for thisComponent in var_0_5Components:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# -------Start Routine "var_0_5"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = var_0_5Clock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *image_4* updates
    if t >= 0.0 and image_4.status == NOT_STARTED:
        # keep track of start time/frame for later
        image_4.tStart = t
        image_4.frameNStart = frameN  # exact frame index
        image_4.setAutoDraw(True)
    frameRemains = 0.0 + 120.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if image_4.status == STARTED and t >= frameRemains:
        image_4.setAutoDraw(False)
    
    # *dots_4* updates
    if t >= 0.0 and dots_4.status == NOT_STARTED:
        # keep track of start time/frame for later
        dots_4.tStart = t
        dots_4.frameNStart = frameN  # exact frame index
        dots_4.setAutoDraw(True)
    frameRemains = 0.0 + 120.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if dots_4.status == STARTED and t >= frameRemains:
        dots_4.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in var_0_5Components:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "var_0_5"-------
for thisComponent in var_0_5Components:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

# ------Prepare to start Routine "rest"-------
t = 0
restClock.reset()  # clock
frameN = -1
continueRoutine = True
routineTimer.add(60.000000)
# update component parameters for each repeat
# keep track of which components have finished
restComponents = [image_2, dots_2]
for thisComponent in restComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# -------Start Routine "rest"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = restClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *image_2* updates
    if t >= 0.0 and image_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        image_2.tStart = t
        image_2.frameNStart = frameN  # exact frame index
        image_2.setAutoDraw(True)
    frameRemains = 0.0 + 60.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if image_2.status == STARTED and t >= frameRemains:
        image_2.setAutoDraw(False)
    
    # *dots_2* updates
    if t >= 0.0 and dots_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        dots_2.tStart = t
        dots_2.frameNStart = frameN  # exact frame index
        dots_2.setAutoDraw(True)
    frameRemains = 0.0 + 60.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if dots_2.status == STARTED and t >= frameRemains:
        dots_2.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in restComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "rest"-------
for thisComponent in restComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

# ------Prepare to start Routine "var_0"-------
t = 0
var_0Clock.reset()  # clock
frameN = -1
continueRoutine = True
routineTimer.add(120.000000)
# update component parameters for each repeat
dots_5.setFieldCoherence(0)
# keep track of which components have finished
var_0Components = [image_5, dots_5]
for thisComponent in var_0Components:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# -------Start Routine "var_0"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = var_0Clock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *image_5* updates
    if t >= 0.0 and image_5.status == NOT_STARTED:
        # keep track of start time/frame for later
        image_5.tStart = t
        image_5.frameNStart = frameN  # exact frame index
        image_5.setAutoDraw(True)
    frameRemains = 0.0 + 120.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if image_5.status == STARTED and t >= frameRemains:
        image_5.setAutoDraw(False)
    
    # *dots_5* updates
    if t >= 0.0 and dots_5.status == NOT_STARTED:
        # keep track of start time/frame for later
        dots_5.tStart = t
        dots_5.frameNStart = frameN  # exact frame index
        dots_5.setAutoDraw(True)
    frameRemains = 0.0 + 120.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if dots_5.status == STARTED and t >= frameRemains:
        dots_5.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in var_0Components:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "var_0"-------
for thisComponent in var_0Components:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)


# completed 5 repeats of 'repeat'


# ------Prepare to start Routine "rest"-------
t = 0
restClock.reset()  # clock
frameN = -1
continueRoutine = True
routineTimer.add(60.000000)
# update component parameters for each repeat
# keep track of which components have finished
restComponents = [image_2, dots_2]
for thisComponent in restComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# -------Start Routine "rest"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = restClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *image_2* updates
    if t >= 0.0 and image_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        image_2.tStart = t
        image_2.frameNStart = frameN  # exact frame index
        image_2.setAutoDraw(True)
    frameRemains = 0.0 + 60.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if image_2.status == STARTED and t >= frameRemains:
        image_2.setAutoDraw(False)
    
    # *dots_2* updates
    if t >= 0.0 and dots_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        dots_2.tStart = t
        dots_2.frameNStart = frameN  # exact frame index
        dots_2.setAutoDraw(True)
    frameRemains = 0.0 + 60.0- win.monitorFramePeriod * 0.75  # most of one frame period left
    if dots_2.status == STARTED and t >= frameRemains:
        dots_2.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in restComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "rest"-------
for thisComponent in restComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# these shouldn't be strictly necessary (should auto-save)
#thisExp.saveAsWideText(filename+'.csv')
#thisExp.saveAsPickle(filename)
logging.flush()
# make sure everything is closed down
thisExp.abort()  # or data files will save again on exit
win.close()
core.quit()
