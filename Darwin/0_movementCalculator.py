#!/user/bin/python
'''
Follow a marker with distance based accelleration
TODO: react to beats
TODO: do not attempt to see things outside of physical FOV (increase vertical FOV?)
Gets data from a ZMQ topic
'''

import time, math, SimpleCV
from globalVars import CHANNEL_TARGETDATA
from globalVars import CHANNEL_BEATDATA
from globalVars import BOT_ARDUINO_ADDRESS as ARDUINO_ADDRESS
from globalVars import BOT_ARDUINO_BAUDRATE as ARDUINO_BAUDRATE

# Functions for Arduino communication
import arduinoInterface as aI

# ZMQ settings
import zmq

# Target channel:
context = zmq.Context()
targetChannel = context.socket(zmq.SUB)
conflate = 1
targetChannel.setsockopt(zmq.CONFLATE, 1 ) # this tells the subscriber to only get the last message sent since the publisher is much faster
targetChannel.setsockopt(zmq.SUBSCRIBE, '')
targetChannel.connect(CHANNEL_TARGETDATA)

targetPoller = zmq.Poller()
targetPoller.register(targetChannel, zmq.POLLIN)

# Beat channel:
context = zmq.Context()
beatChannel = context.socket(zmq.SUB)
beatChannel.setsockopt(zmq.CONFLATE, 1 ) # TODO: see if this is needed as it is possible to miss crucial beat data this way
beatChannel.setsockopt(zmq.SUBSCRIBE, '')
beatChannel.connect(CHANNEL_BEATDATA)

beatPoller = zmq.Poller()
beatPoller.register(beatChannel, zmq.POLLIN)

printing = False
print_response = False
testDelay = True # Controls whether the script counts down 10 seconds before executing tasks

dt = 0.0001

vmin = 0.01
maxV = 4.00
a = 0.015
a_search = 0.1

vmax = [maxV, maxV, maxV, maxV]
vCurr = [vmin, vmin, vmin, vmin]

# position format: (joint0, joint1, joint2, joint3)
pos             = [ 94.0, 155.0, 98.0, 145.0]
pos_default     = ( 94.0, 155.0, 98.0, 145.0)
pos_search      = ( 94.0, 125.0, 98.0, 175.0)
pos_search_left = (  0.0, 125.0, 98.0, 175.0)
pos_search_right= (180.0, 125.0, 98.0, 175.0)
braking = [False, False, False, False]

# Modifiers for beat response
beatMod = {
            'mod'   : 10,  # degrees of modification +/-
            'dir'   : 0    # direction of modification. can be -1 | 0 | 1
          }

# Calculates the stopping distance based on the velocity given
# @param double vCurr: velocity to stop from
def stoppingDistance(vCurr):
    d_stop = (-(vCurr * vCurr)) / (2.0 * -a)      # -a because we're stopping
    if printing: print "d_stop:" + str(round(d_stop,2)) +"\t",
    return d_stop


# Function to determine remaining movement distance
# @param pos:  current position
# @param goal: target position
# @return: double d_rem: distance remaining
def distanceRemaining(pos, goal):
    d_rem = abs(goal - pos)
    if printing: print "d_rem:" + str(round(d_rem,2)) +"\t",
    return d_rem


# determines the relative maximume velocities needed to finish all movement at the same time
# @param list pos: a list of current positions
# @param list goal: the target positions
def determineVmax(pos, goal):
    global vmax, maxV
    d_rem = []
    for i in range(len(pos)):
        d_rem.append(distanceRemaining(pos[i], goal[i]))
    
    i_max = d_rem.index(max(d_rem))
    if d_rem[i_max] == 0: return
    vmax[i_max] = maxV
    
    for j in range(4):
        if not j == i_max:
            vmax[j] = d_rem[j] / d_rem[i_max] / maxV


# Function to determine the speed of the joints
# @param list pos: the current joint positions
# @param list goal: the target positions
# @param i the index of the currently used point {needed for global vCurr}
def determineSpeed(pos, goal, i):
    global vCurr, vmax, vmin, a, braking, searching
    
    # if searching the a can be larger
    _a = a
    if searching: _a = a_search
    
    if distanceRemaining(pos[i], goal[i]) < stoppingDistance(vCurr[i]):
        braking[i] = True
    
    if not braking[i]:
        if vCurr[i] < vmax[i]:
            if vCurr[i]+_a > vmax[i]:
                vCurr[i] = vmax[i]
            else:
                vCurr[i]+=_a
    else:
        if vCurr[i] > vmin:
            if vCurr[i]-_a < vmin:
                vCurr[i] = vmin
                print "minimum speed"
            else:
                vCurr[i]-=_a
                    
    if printing: print "vCurr:" + str(round(vCurr[i],2)) +"\t",
    return vCurr[i]


# Compare two lists and determine whether their contents are equal
# @param list list1: some list of arbitrary length
# @param list list2: some list of the same length
def done(list1, list2):
    if len(list1)!=len(list2): return False
    
    done_count = 0
    
    for i in range(len(list1)):
        if abs(list1[i] - list2[i]) < vmin * 3: #A bit of tolerance is needed to prevent infinite loops
            done_count+=1
        
            
    if done_count == len(list1):
        return True
    else:
        return False
        
# Compare two inputs, being lists or variables. Must be of the same type or it will return false by default
# @param in1: some input variable
# @param in2: some input variable
def done2(in1, in2):
    if type(in1) != type(in2):
        print "Unequal types: ",
        print type(in1),type(in2)
        return False
    
    if type(in1) is 'list':
        return done(in1, in2)
    elif abs(in1 - in2) < vmin*3:
        return True
    return False

# Function to move the current position of the motors
# @param list pos: the list of current positions
# @param list end_pose: the list of desired end poses
def move(pos, end_pose):
    global braking, beatMod
    
    # modify the end pose with the beat
    tar_pose = [end_pose[0], end_pose[1] + (beatMod['mod'] * beatMod['dir']), \
                end_pose[2], end_pose[3] - (beatMod['mod'] * beatMod['dir'])]   # 1 and 3 are opposed, hence + & -
    
    if not done(pos, tar_pose):
        determineVmax(pos, tar_pose)
        
        for i in range(len(pos)):
            if abs(pos[i] - tar_pose[i]) > vmin * 5:
                #there are some odd issues with the braking triggers not resetting properly
                if abs(pos[i] - tar_pose[i]) > vmin *10:
                    braking[i] = False
                
                v = determineSpeed(pos, tar_pose, i)
                
                if pos[i] < tar_pose[i]:
                    pos[i]+=v
                else:
                    pos[i]-=v
            else:
                pos[i] = tar_pose[i]
                braking[i] = False
            
            r = aI.arduinoWrite(pos[i], i)
            if print_response: print r
        if printing: print "."

# Arduino-style millis() function for timekeeping
millis = lambda: int(round(time.time() * 1000))

#############################################################
#                   RUNNING CODE BELOW                      #
#############################################################

r = aI.arduinoConnect(ARDUINO_ADDRESS, ARDUINO_BAUDRATE)
if print_response: print r

tar_x = 0
tar_y = 0
deg_x = 0
deg_y = 0
findTime = 0
t_thresh = 1500
searching = False
searchDir = 1
targetData = {
                't'       : millis(),
                'findTime': 0,
                'found'   : False,
                'tar_px'  : {'x':0.0, 'y':0.0},
                'tar_dg'  : {'x':0.0, 'y':0.0}
            }
startTime = millis()
lastLoop = 0

while True: 
    if testDelay:
        for i in range(10):
            print 10-i
            time.sleep(1)
        testDelay = False
        
    # TODO: This is a bit of a hack. Find out whether the poller can return a json instead.
    if len(targetPoller.poll(1)) is not 0:
        targetData = targetChannel.recv_json()
    if len(beatPoller.poll(1)) is not 0:
        beatData = beatChannel.recv_json()
        
        # if the beat is not there, don't use the beat
        if beatData['s0'] < 10:
            beatMod['dir'] = 0
        elif beatMod['dir'] == 0:
            beatMod['dir'] = -1
            
        # if a beat is detected, respond by switching direction
        if beatData['beat']:
            print "Beat!"
            if beatMod['dir'] == 1:
                beatMod['dir'] = -1
            elif beatMod['dir'] == -1:
                beatMod['dir'] = 1
 
    if targetData['found']:
        searching = False
        deg_x = targetData['tar_dg']['x'] 
        deg_y = targetData['tar_dg']['y']
        findTime = targetData['findTime']
        print "Hit!"
    elif millis() - findTime > t_thresh and not searching:
        braking = [False, False, False, False]
        move(pos, pos_search)
        if done2(pos[0], pos_search[0]):
            searching = True
            print "Searching!"
        continue            
    elif searching:
        if searchDir == 1: 
            move(pos, pos_search_left)
            if done2(pos[0], pos_search_left[0]):  # only the bottom motor is used for this
                searchDir = -1
                print "Looking left now."
        else:
            move(pos, pos_search_right)
            if done2(pos[0], pos_search_right[0]): # only the bottom motor is used for this
                searchDir = 1
                print "Looking right now."
        continue
      
    
    newpos = (pos[0] + deg_x, pos[1], pos[2], pos[3] - deg_y)       # TODO: This causes a bit of a quirk with the beat modification
        
    move(pos, newpos)
