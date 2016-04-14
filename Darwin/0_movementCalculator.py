#!/user/bin/python
'''
Follow a marker with distance based accelleration
TODO: react to beats
TODO: do not attempt to see things outside of physical FOV (increase vertical FOV?)
Gets data from a ZMQ topic
'''

import time, math, SimpleCV

# Functions for Arduino communication
import arduinoInterface
ARDUINO_ADDRESS = '/dev/ttyACM3'

# ZMQ settings
import zmq
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, '')
socket.connect("tcp://127.0.0.1:4002") # targetData topic

printing = True
print_response = False

dt = 0.0001

vmin = 0.01
maxV = 4.00
a = 0.15

vmax = [maxV, maxV, maxV, maxV]
vCurr = [vmin, vmin, vmin, vmin]

arduino = None

# position format: (joint0, joint1, joint2, joint3)
pos = [94, 155, 98, 145]
pos_default = (94, 155, 98, 145)
pos_search = (94, 125, 98, 175)
pos_search_left = (0, 125, 98, 175)
pos_search_right = (180, 125, 98, 175)
braking = [False, False, False, False]


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
    global vCurr, vmax, vmin, a, braking
    
    if distanceRemaining(pos[i], goal[i]) < stoppingDistance(vCurr[i]):
        braking[i] = True
    
    if not braking[i]:
        if vCurr[i] < vmax[i]:
            if vCurr[i]+a > vmax[i]:
                vCurr[i] = vmax[i]
            else:
                vCurr[i]+=a
    else:
        if vCurr[i] > vmin:
            if vCurr[i]-a < vmin:
                vCurr[i] = vmin
                print "minimum speed"
            else:
                vCurr[i]-=a
                    
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


# Function to move the current position of the motors
# @param list pos: the list of current positions
# @param list end_pose: the list of desired end poses
def move(pos, end_pose):
    global braking
    if not done(pos, end_pose):
        determineVmax(pos, end_pose)
        
        for i in range(len(pos)):
            if abs(pos[i] - end_pose[i]) > vmin * 5:
                #there are some odd issues with the braking triggers not resetting properly
                if abs(pos[i] - end_pose[i]) > vmin *10:
                    braking[i] = False
                
                v = determineSpeed(pos, end_pose, i)
                
                if pos[i] < end_pose[i]:
                    pos[i]+=v
                else:
                    pos[i]-=v
            else:
                pos[i] = end_pose[i]
                braking[i] = False
            
            r = arduinoWrite(pos[i], i)
            if print_response: print r
        if printing: print "."

# Arduino-style millis() function for timekeeping
millis = lambda: int(round(time.time() * 1000))

#############################################################
#                   RUNNING CODE BELOW                      #
#############################################################

r = arduinoConnect(ARDUINO_ADDRESS)
if print_response: print r

tar_x = 0
tar_y = 0
deg_x = 0
deg_y = 0
findTime = 0
t_thresh = 1500
searching = False
searchDir = 1

startTime = millis()
lastLoop = 0

while True: 
    targetData = socket.recv_json()
    
    if targetData is not None:
        searching = !targetData['found']
        deg_x = targetData['tar_dg']['x'] 
        deg_y = targetData['tar_dg']['y']
        findTime = targetData['findTime']
        print "Hit!"
    elif millis() - findTime > t_thresh and not searching:
        
        braking = [False, False, False, False]
        move(pos, pos_search)
        if done(pos, pos_search):
            searching = True
            print "Searching!"
        continue            
    elif searching:
        if searchDir == 1: 
            move(pos, pos_search_left)
            if done(pos, pos_search_left):
                searchDir = -1
                print "Looking left now."
        else:
            move(pos, pos_search_right)
            if done(pos, pos_search_right):
                searchDir = 1
                print "Looking right now."
        continue
      
    
    newpos = (pos[0] + deg_x, pos[1], pos[2], pos[3] - deg_y)
        
    move(pos, newpos)
