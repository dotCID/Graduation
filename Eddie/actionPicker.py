#!/user/bin/python
'''
This script picks and executes Actions based on external inputs and a RNG. This is an infinitely looping script.
'''

import zmq, time, math, random

## Actions
from Actions import Action
from Actions import Action_Contact
from Actions import Action_Scan
from Actions import Action_Focus
from Actions import Action_Stevie
from Actions import Action_Bored

## Global Variables
from globalVars import CHANNEL_MOVEMENTDATA
from globalVars import CHANNEL_ENERGYDATA
from globalVars import CHANNEL_TARGETDATA
from globalVars import CHANNEL_MODE
from globalVars import MARGIN_USER_CONTACT
from globalVars import printing

# Exit codes for the actions
from globalVars import EXIT_CODE_DONE
from globalVars import EXIT_CODE_ERROR

from globalVars import EXIT_CODE_CONTACT
from globalVars import EXIT_CODE_SCAN
from globalVars import EXIT_CODE_FOCUS
from globalVars import EXIT_CODE_STEVIE
from globalVars import EXIT_CODE_BORED


""" *** Communication Setup *** """
## ZMQ Movement Data channel - Provides data on user position
mv_context = zmq.Context()
movementChannel = mv_context.socket(zmq.SUB)
movementChannel.setsockopt(zmq.CONFLATE, 1 ) # this tells the subscriber to only get the last message sent since the publisher is probably faster
movementChannel.setsockopt(zmq.SUBSCRIBE, '')
movementChannel.connect(CHANNEL_MOVEMENTDATA)

movementPoller = zmq.Poller()
movementPoller.register(movementChannel, zmq.POLLIN)

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

## Actions
''' **** NOTE THAT THESE MUST HAVE THE SAME INDEX IN THIS ARRAY AS THEIR NORMAL EXIT CODE **** '''
actions = [
            Action.Action(), # to prevent confusion this is a spacer
            Action_Contact.SpecificAction(),
            Action_Scan.SpecificAction(),
            Action_Focus.SpecificAction(),
            Action_Stevie.SpecificAction(),
            Action_Bored.SpecificAction()
          ]

## Helper Functions
"""Arduino-style millis() function for timekeeping"""
millis = lambda: int(round(time.time() * 1000))

## Variables
movementData = {
                't'       : millis(),
                'deg_x'   : 180.0,
                'deg_y'   : 180.0,
                'deg_z'   : 180.0
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
                'eg_label' : "none"
               }

exit_code = EXIT_CODE_DONE

def randomSelect(chances, modes):
    """
    Selects an action from the given set and sets the corresponding mode via ZMQ.
    @param num: the selection number, between 0.0 and 1.0 inclusive
    @param chances: a list of chances for the available actions
    @param modes: the modes to select from
    @return: the index {1..5} of the next action
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
    @return: the index {1..5} of the next action
    """
    chances = (0.0, 0.4, 0.0, 0.0, 0.6)
    modes   = ("0", "B", "0", "0", "B")
    
    return randomSelect(chances, modes)

def randomSelectB():
    """
    Selects an action from set B (low energy).
    @return: the index {1..5} of the next action
    """
    chances = (0.0, 0.3, 0.1, 0.6, 0.0)
    modes   = ("0", "B", "B", "B", "0")
    
    return randomSelect(chances, modes)

def randomSelectC():
    """
    Selects an action from set C (high energy).
    @return: the index {1..5} of the next action
    """
    chances = (0.0, 0.3, 0.7, 0.0, 0.0)
    modes   = ("0", "A", "A", "0", "0")
    
    return randomSelect(chances, modes)

#############################################################
#                   RUNNING CODE BELOW                      #
#############################################################


while True:
    ## Read ZMQ inputs
    if len(movementPoller.poll(0)) is not 0:
        movementData = movementChannel.recv_json()
    
    user_contact_angles = actions[0].getUserContactAngles()
    
    ## Check whether the user might contact the bot
    if ((user_contact_angles['deg_x'] <= movementData['deg_x'] + MARGIN_USER_CONTACT ) and \
        (user_contact_angles['deg_x'] >= movementData['deg_x'] - MARGIN_USER_CONTACT )) and \
       ((user_contact_angles['deg_y'] <= movementData['deg_y'] + MARGIN_USER_CONTACT ) and \
        (user_contact_angles['deg_y'] >= movementData['deg_y'] - MARGIN_USER_CONTACT )) and \
       ((user_contact_angles['deg_z'] <= movementData['deg_z'] + MARGIN_USER_CONTACT ) and \
        (user_contact_angles['deg_z'] >= movementData['deg_z'] - MARGIN_USER_CONTACT )):
        if printing: print "Possible attention!"
        #exit_code = actions[2].execute()
        #continue
    
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
            exit_code = actions[nextAction].execute()
            continue
        elif energyData['eg_label'] == "low":
            nextAction = randomSelectB()
            if printing: print "Randomly selected", nextAction
            exit_code = actions[nextAction].execute()
            continue
        elif energyData['eg_label'] == "high":
            nextAction = randomSelectC()
            if printing: print "Randomly selected", nextAction
            exit_code = actions[nextAction].execute()
            continue
    elif exit_code is EXIT_CODE_ERROR:
        print "Something went very wrong. Entering an infinite loop."
        while True:
            pass
    else:
        # if an Action returns anything other than EXIT_CODE_DONE we follow their advice:
        if printing: print "Continuing ", exit_code
        exit_code = actions[exit_code].execute()

        continue
