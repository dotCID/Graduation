#!/user/bin/python
'''
This script picks and executes Actions based on external inputs and a RNG. This is an infinitely looping script.
'''

import zmq, time, math, random, sys

## Actions
from Actions import Action
from Actions import Action_Contact
from Actions import Action_Scan
from Actions import Action_Acknowledge
from Actions import Action_Stevie
from Actions import Action_Bored

## Global Variables
from globalVars import CHANNEL_IMU_RAWPOS
from globalVars import CHANNEL_ENERGYDATA
from globalVars import CHANNEL_TARGETDATA
from globalVars import CHANNEL_MODE
from globalVars import CHANNEL_PEDAL

from globalVars import MARGIN_USER_CONTACT
from globalVars import printing
from globalVars import TEST_MODE_SLOW

# Exit codes for the actions
from globalVars import EXIT_CODE_DONE
from globalVars import EXIT_CODE_ERROR

from globalVars import EXIT_CODE_CONTACT
from globalVars import EXIT_CODE_SCAN
from globalVars import EXIT_CODE_ACK
from globalVars import EXIT_CODE_STEVIE
from globalVars import EXIT_CODE_BORED

## Change terminal window header for easier identification of contents
sys.stdout.write("\x1b]2;actionPicker.py\x07")

""" *** Communication Setup *** """
## ZMQ Raw orientation channel - Provides data on user orientation
mv_context = zmq.Context()
orientationChannel = mv_context.socket(zmq.SUB)
orientationChannel.setsockopt(zmq.CONFLATE, 1 ) # this tells the subscriber to only get the last message sent since the publisher is probably faster
orientationChannel.setsockopt(zmq.SUBSCRIBE, '')
orientationChannel.connect(CHANNEL_IMU_RAWPOS)

orientationPoller = zmq.Poller()
orientationPoller.register(orientationChannel, zmq.POLLIN)

## ZMQ Energy Data channel - Provides data on music energy
eg_context = zmq.Context()
energyChannel = eg_context.socket(zmq.SUB)
energyChannel.setsockopt(zmq.CONFLATE, 1 )
energyChannel.setsockopt(zmq.SUBSCRIBE, '')
energyChannel.connect(CHANNEL_ENERGYDATA)

energyPoller = zmq.Poller()
energyPoller.register(energyChannel, zmq.POLLIN)

## ZMQ Target Data channel - Provides data on the last sighting of our tag
tg_context = zmq.Context()
targetChannel = tg_context.socket(zmq.SUB)
targetChannel.setsockopt(zmq.CONFLATE, 1 )
targetChannel.setsockopt(zmq.SUBSCRIBE, '')
targetChannel.connect(CHANNEL_TARGETDATA)

targetPoller = zmq.Poller()
targetPoller.register(targetChannel, zmq.POLLIN)

## ZMQ Mode Channel - Provides the currently set mode
mode_context = zmq.Context()
mode_socket = mode_context.socket(zmq.PUB)
mode_socket.bind(CHANNEL_MODE)

## ZMQ Pedal Channel - provides the current state of the foot pedal
ped_context = zmq.Context()
pedChannel = ped_context.socket(zmq.SUB)
pedChannel.setsockopt(zmq.CONFLATE, 1 )
pedChannel.setsockopt(zmq.SUBSCRIBE, '')
pedChannel.connect(CHANNEL_PEDAL)

pedPoller = zmq.Poller()
pedPoller.register(pedChannel, zmq.POLLIN)

oldPedalState = None

## Actions
''' **** NOTE THAT THESE MUST HAVE THE SAME INDEX IN THIS ARRAY AS THEIR NORMAL EXIT CODE **** '''
actions = [
            Action.Action(), # to prevent confusion this is a spacer
            Action_Contact.SpecificAction(),
            Action_Scan.SpecificAction(),
            Action_Acknowledge.SpecificAction(),
            Action_Stevie.SpecificAction(),
            Action_Bored.SpecificAction()
          ]

## Helper Functions
"""Arduino-style millis() function for timekeeping"""
millis = lambda: int(round(time.time() * 1000))

## Variables
orientationData = {
                't'       : millis(),
                'x'   : 180.0,
                'y'   : 180.0,
                'z'   : 180.0
               }
targetData   = {
                't'       : millis(),
                'findTime': 0,
                'found'   : False,
                'tar_px'  : {'x':0.0, 'y':0.0},
                'tar_dg'  : {'x':0.0, 'y':0.0}
               }
energyData   = {
                't'        : millis(),
                'energy'   : 0.0,
                'eg_label' : "low"
               }


def randomSelect(chances, modes):
    """
    Selects an action from the given set and sets the corresponding mode via ZMQ.
    @param num: the selection number, between 0.0 and 1.0 inclusive
    @param chances: a list of chances for the available actions
    @param modes: the modes to select from
    @return: the return code {1..5} of the next action
    """
    choice = random.random() #note that 1.0 is not possible?
    
    cum_chance = 0.0
    for i in range(len(chances)):
        if choice < chances[i]+cum_chance:
            mode_message = {
                           't'   : millis(),
                           'mode': modes[i]
                           }
            mode_socket.send_json(mode_message)
            return i+1
        else:
            cum_chance += chances[i]

def randomSelectA():
    """
    Selects an action from set A (no energy).
    @return: the return code {2 or 5} of the next action
    """
    chances = (0.0, 0.4, 0.0, 0.0, 0.6)
    modes   = ("0", "B", "0", "0", "B")
    
    return randomSelect(chances, modes)

def randomSelectB():
    """
    Selects an action from set B (low energy).
    @return: the return code {2, or 4} of the next action
    """
    chances = (0.0, 0.4, 0.0, 0.6, 0.0)
    modes   = ("0", "B", "0", "B", "0")
    
    return randomSelect(chances, modes)

def randomSelectC():
    """
    Selects an action from set C (high energy).
    @return: the return code {2 or 3} of the next action
    """
    chances = (0.0, 0.3, 0.7, 0.0, 0.0)
    modes   = ("0", "A", "A", "0", "0")
    
    return randomSelect(chances, modes)

def getPedalState():
    """
    Gets the current state of the foot pedal
    """
    global oldPedalState
    if len(pedPoller.poll(0)) is not 0:
        pedData = pedChannel.recv_json()
    
        return pedData['state']
    else: return oldPedalState

#############################################################
#                   RUNNING CODE BELOW                      #
#############################################################

exit_code = 0 # start without movement
waiting = False
dead = False

oldPedalState = getPedalState()

while True:
    if exit_code == -1:
        ## Start in user input mode at default position
        while waiting:
            e = actions[0].execute(150)
            if e == 0:
                waiting = False
        
        var = int(raw_input("Waiting to start.\nEnter an exit code to start execution:\n"))
        if var >= -2 and var <= 4:
            exit_code = var
            waiting = True
            continue
            
    if exit_code == -2:
        while not dead:
            e = actions[0].playDead()
            if e == 0:
                dead = True
        
        var = int(raw_input("Playing Dead.\nEnter an exit code to start be alive:\n"))
        if var >= -1 and var <= 4:
            actions[0].alive()
            exit_code = var
            dead = False
            continue
        

    ## Read ZMQ inputs
    if len(orientationPoller.poll(0)) is not 0:
        orientationData = orientationChannel.recv_json()
    
    user_contact_angles = actions[0].getUserContactAngles()
    
    ## Check whether the user might contact the bot and whether we're not already making contact
    if ((user_contact_angles['x'] <= orientationData['x'] + MARGIN_USER_CONTACT )  and \
        (user_contact_angles['x'] >= orientationData['x'] - MARGIN_USER_CONTACT )) and \
       ((user_contact_angles['y'] <= orientationData['y'] + MARGIN_USER_CONTACT )  and \
        (user_contact_angles['y'] >= orientationData['y'] - MARGIN_USER_CONTACT )) and \
       ((user_contact_angles['z'] <= orientationData['z'] + MARGIN_USER_CONTACT )  and \
        (user_contact_angles['z'] >= orientationData['z'] - MARGIN_USER_CONTACT )) and \
        exit_code != 1 and exit_code != 2:
        if printing: print "Possible attention!", exit_code
        exit_code = actions[2].execute()
        continue
        
    ## Support for foot pedal:
    pedalState = getPedalState()
    if pedalState != oldPedalState:
        if printing: print "Foot pedal was pressed!"
        print "old:", oldPedalState, " new:", pedalState
        oldPedalState = pedalState
        exit_code = actions[1].execute()
        continue
        
    ## Check whether we need to consult the camera for unexpected contact
    if (exit_code is not EXIT_CODE_CONTACT) and (exit_code is not EXIT_CODE_SCAN):
       # if printing: print "Checking camera."
        
        if len(targetPoller.poll(0)) is not 0:
            targetData = targetChannel.recv_json()
        if targetData['found']:
            exit_code = actions[1].execute()
            if printing: print "Someone sees me!"
            continue

    ## Is our last action completed?
    if exit_code is EXIT_CODE_DONE:
        if len(energyPoller.poll(0)) is not 0:
            energyData = energyChannel.recv_json()
        
        if energyData['eg_label'] == "none":
            nextAction = randomSelectA()
            if printing: print "Randomly selected", nextAction
            exit_code = actions[nextAction].execute(250)
            if TEST_MODE_SLOW: time.sleep(1)
            continue
        elif energyData['eg_label'] == "low":
            nextAction = randomSelectB()
            if printing: print "Randomly selected", nextAction
            exit_code = actions[nextAction].execute(250)
            if TEST_MODE_SLOW: time.sleep(1)
            continue
        elif energyData['eg_label'] == "high":
            nextAction = randomSelectC()
            if printing: print "Randomly selected", nextAction
            exit_code = actions[nextAction].execute(250)
            if TEST_MODE_SLOW: time.sleep(1)
            continue
    elif exit_code is EXIT_CODE_ERROR:
        print "Something went very wrong. Entering an infinite loop."
        while True:
            pass
    else:
        # if an Action returns anything other than EXIT_CODE_DONE we follow their advice:
        #if printing: print "Continuing ", exit_code
        if exit_code == EXIT_CODE_ACK:
            exit_code = actions[exit_code].execute(450)
        else:
            exit_code = actions[exit_code].execute(250)

        continue
