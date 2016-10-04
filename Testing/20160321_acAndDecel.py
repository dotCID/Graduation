#!/usr/bin/python
import time

'''
The functions in this file control the speed of 4 virtual motors depending on the accelleration and deceleration parameter a and the maximum allowed speed, maxV.
They attempt to finish at the same time by calculating the maximum speed per motor depending on the distance its effector needs to travel.

The motion is between two pre-determined poses with motor positions.

'''

printing = False

dt = 0.25

vmin = 0.05
maxV = 3.00
vmax = [maxV, maxV, maxV, maxV]
vCurr = [vmin, vmin, vmin, vmin]

a = 0.05

# position format: (joint0, joint1, joint2, joint3)
pos = [80, 120, 80, 120]
breaking = [False, False, False, False]

pose_1 = (15, 165, 30, 160)
pose_2 = (165, 15, 150, 20)

def stoppingDistance(vCurr):
    d_stop = (-(vCurr * vCurr)) / (2 * -a)      # -a because we're stopping
    if printing: print "d_stop:" + str(round(d_stop,2)) +"\t",
    return d_stop

# @param pos:  current position
# @param goal: target position
def distanceRemaining(pos, goal):
    d_rem = abs(goal - pos)
    if printing: print "d_rem:" + str(round(d_rem,2)) +"\t",
    return d_rem

# determines the relative maximume velocities needed to finish all movement at the same time
def determineVmax(pos, goal):
    global vmax, maxV
    d_rem = [distanceRemaining(pos[0], goal[0]), \
             distanceRemaining(pos[1], goal[1]), \
             distanceRemaining(pos[2], goal[2]), \
             distanceRemaining(pos[3], goal[3])]
    
    i_max = d_rem.index(max(d_rem))
    vmax[i_max] = maxV
    
    for j in range(4):
        if not j == i_max:
            vmax[j] = d_rem[j] / d_rem[i_max] / maxV

def determineSpeed(pos, goal, i):
    # do we need to break yet?
    
    #if we haven't reached the breaking point
        #if we're not moving at max speed
            #accellerate
        #else
            #do nothing
    #else
        #if we're not moving at min speed
            #decelerate
        #else
            #do nothing
    global vCurr, vmax, vmin, a
    
    if distanceRemaining(pos[i], goal[i]) < stoppingDistance(vCurr[i]):
        breaking[i] = True
    
    if not breaking[i]:
        if vCurr[i] < vmax[i]:
            if vCurr[i]+a > vmax[i]:
                vCurr[i] = vmax[i]
            else:
                vCurr[i]+=a
    else:
        if vCurr[i] > vmin:
            if vCurr[i]-a < vmin:
                vCurr[i] = vmin
            else:
                vCurr[i]-=a
                    
    if printing: print "vCurr:" + str(round(vCurr[i],2)) +"\t",
    return vCurr[i]

def done(list1, list2):
    done_count = 0
    
    for i in range(len(list1)):
        if list1[i] == list2[i]:
            done_count+=1
            
    if done_count == len(list1):
        return True
    else:
        return False

def move(pos, end_pose):
    #for each joint
        #if we're not at the target yet
            #adjust speed            
            #change position
        #else
            #release the brakes but don't move
    
    while not done(pos, end_pose):
        determineVmax(pos, end_pose)
        
        for i in range(len(pos)):
            if abs(pos[i] - end_pose[i]) > vmin:
                
                v = determineSpeed(pos, end_pose, i)
                
                if pos[i] < end_pose[i]:
                    pos[i]+=v
                else:
                    pos[i]-=v
            else:
                pos[i] = end_pose[i]
                breaking[i] = False
        if printing: print "."
        time.sleep(dt)

move(pos, pose_1)
print " ========================== "
time.sleep(3)
move(pos, pose_2)
print " ========================== "
time.sleep(3)
print "done."
