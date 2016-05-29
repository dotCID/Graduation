#!/user/bin/python
'''
This is the base class for Actions performed by Eddie and beyond. It is loosely based on the motionController.py script found in previous iterations.

This script is meant for 3-servo robot models, as opposed to the 4-servo models Charles and Darwin where one servo was not used.

The intention is for all actions that can be selected by the Action Picker to have a similar interface.
'''
import time
import arduinoInterface as aI # This will replace the JointData channel. All subclasses share access to this interface and it contains the current joint data

import zmq

## Exit codes for the actions
from globalVars import EXIT_CODE_DONE
from globalVars import EXIT_CODE_ERROR
from globalVars import EXIT_CODE_CONTACT
from globalVars import EXIT_CODE_SCAN
from globalVars import EXIT_CODE_FOCUS
from globalVars import EXIT_CODE_STEVIE
from globalVars import EXIT_CODE_BORED

## Address data
from globalVars import BOT_ARDUINO_ADDRESS as ARDUINO_ADDRESS
from globalVars import BOT_ARDUINO_BAUDRATE as ARDUINO_BAUDRATE

## Other
from globalVars import printing
from globalVars import TEST_MODE_SLOW
from globalVars import CHANNEL_MODE

## Pose data
from poses import pos_default
from poses import pos_min
from poses import pos_max

loc_printing = False

class Action:
    ## Last known user positions. Accessible from subclasses via Action.*
    user_contact_angles = {
                            't' : 0,
                            'deg_x' : 350.0,
                            'deg_y' : 5.0,
                            'deg_z' : -180.0
                          }
    contact_joint_positions     = [ 94.0 , 75.0, 90.0 ]

    def __init__(self):
        # Output control
        self.printing = False
        
        # Testing settings
        self.testDelay= False
        
        # Speed settings
        self.minV     = 0.01
        self.maxV     = 2.00
        self.a        = 0.0075
        self.vMax     = [self.maxV, self.maxV, self.maxV]
        self.vCurr    = [self.minV, self.minV, self.minV]
        self.mode     = "A"
        self.braking  = [False, False, False]
        
        # Modifiers for beat response
        self.beatMod = {
                        'mod'   : 10,  # degrees of modification +/-
                        'dir'   : 0    # direction of modification. can be -1 | 0 | 1
                       }
        # Position
        self.pos_target     = list(pos_default)
        
        # Looping variables
        self.loops_executed = 0
        self.max_loops = 0
        
        # Initialise the Arduino
        r = aI.arduinoConnect(ARDUINO_ADDRESS, ARDUINO_BAUDRATE)
        if printing: print "Action: Arduino response:",r
        
        # Initialise ZMQ MODE channel:
        self.md_context = zmq.Context()
        self.modeChannel = self.md_context.socket(zmq.SUB)
        self.modeChannel.setsockopt(zmq.CONFLATE, 1 )
        self.modeChannel.setsockopt(zmq.SUBSCRIBE, '')
        self.modeChannel.connect(CHANNEL_MODE)
        self.modePoller = zmq.Poller()
        self.modePoller.register(self.modeChannel, zmq.POLLIN)
        
    # Arduino-style millis() function for timekeeping
    millis = lambda: int(round(time.time() * 1000))
    
    def currentPosition(self):
        return aI.getAngles()
    
    def stoppingDistance(self, vCurr):
        """
        Calculates the stopping distance based on the velocity given.
        @param double vCurr: velocity to stop from
        """
        
        d_stop = (-(vCurr * vCurr)) / (2.0 * -self.a)      # -a because we're stopping
        if loc_printing: print "d_stop:" + str(round(d_stop,2)) +"\t",
        return d_stop
    
    def distanceRemaining(self, pos, goal):
        """
        Function to determine remaining movement distance
        @param pos:  current position
        @param goal: target position
        @return: double d_rem: distance remaining
        """
        
        d_rem = abs(goal - pos)
        if loc_printing: print "d_rem:" + str(round(d_rem,2)) +"\t",
        return d_rem
    
    def determineVmax(self, pos, goal):
        """
        Determines the relative maximume velocities needed to finish all movement at the same time
        @param list pos: a list of current positions
        @param list goal: the target positions
        """
        
        d_rem = []
        for i in range(len(pos)):
            d_rem.append(self.distanceRemaining(pos[i], goal[i]))
        
        i_max = d_rem.index(max(d_rem))
        if d_rem[i_max] == 0: return
        self.vMax[i_max] = self.maxV
        
        for j in range(3):
            if not j == i_max:
                self.vMax[j] = d_rem[j] / d_rem[i_max] / self.maxV

    def determineSpeed(self, pos, goal, i):
        """
        Function to determine the speed of the joints
        @param list pos: the current joint positions
        @param list goal: the target positions
        @param i the index of the currently used point {needed for global vCurr}
        """
        
        _a = self.a
        
        #if searching: _a = a_search  #TODO: this is a possible improvement for certain actions -> override with a_search >> a
        
        if self.distanceRemaining(pos[i], goal[i]) < self.stoppingDistance(self.vCurr[i]):
            self.braking[i] = True
        
        if not self.braking[i]:
            if self.vCurr[i] < self.vMax[i]:
                if self.vCurr[i]+_a > self.vMax[i]:
                    self.vCurr[i] = self.vMax[i]
                else:
                    self.vCurr[i]+=_a
        else:
            if self.vCurr[i] > self.minV:
                if self.vCurr[i]-_a < self.minV:
                    self.vCurr[i] = self.minV
                    if printing: print "minimum speed"
                else:
                    self.vCurr[i]-=_a
                        
        if loc_printing: print "vCurr:" + str(round(self.vCurr[i],2)) +"\t",
        return self.vCurr[i]
        
    def done_list(self, list1, list2):
        """
        Compare two lists and determine whether their contents are equal
        @param list list1: some list of arbitrary length
        @param list list2: some list of the same length
        """
        
        if len(list1)!=len(list2): return False
        
        done_count = 0
        
        for i in range(len(list1)):
            if abs(list1[i] - list2[i]) < self.minV * 3: #A bit of tolerance is needed to prevent infinite loops
                done_count+=1
            
                
        if done_count == len(list1):
            return True
        else:
            return False
            
    def done(self, in1, in2):
        """
        Compare two inputs, being lists or variables. Must be of the same type or it will return false by default
        @param in1: some input variable
        @param in2: some input variable
        """
        
        if type(in1) != type(in2):
            print "Unequal types: ",
            print type(in1),type(in2)
            return False
        
        if type(in1) is list:
            return  self.done_list(in1, in2)
        elif abs(in1 - in2) < self.minV*3:
            return True
        return False
        
    def getMode(self, oldMode):
        """
        Function to get the latest mode data from the CHANNEL_MODE. If none available, returns the passed old mode.
        @param oldMode: previously set mode, f.i. "A"
        """
        if len(self.modePoller.poll(0)) is not 0:
            return self.modeChannel.recv_json()
        else: return oldMode
        
    def adaptToMode(self):
        """
        Function to adapt the accelleration and minimum and maximum speeds according to the mode broadcast in the CHANNEL_MODE.
        """
        self.mode = self.getMode(self.mode)
        
        #TODO: test optimum values for this
        if self.mode is "A":
            self.minV = 0.01
            self.maxV = 4.00
            self.a = 0.015
            self.vMax = [self.maxV, self.maxV, self.maxV]
        elif self.mode is "B":
            self.minV = 0.05
            self.maxV = 8.00
            self.a = 0.025
            self.vMax = [self.maxV, self.maxV, self.maxV]
        
    def move(self, end_pose):
        """
        Function to change the intended joint positions.
        @param list end_pose: the list of desired end poses
        """
        
        if printing: print "Action: move: end_pose = ",end_pose
        self.adaptToMode()
        
        pos = aI.getAngles() ## This is the new method of getting current joint data
        
        # modify the end pose with the beat
        # 1 and 3 are opposed, hence + & -
        tar_pose = [end_pose[0], end_pose[1] + (self.beatMod['mod'] * self.beatMod['dir']), \
                                 end_pose[2] - (self.beatMod['mod'] * self.beatMod['dir'])]
        
        if not self.done_list(pos, tar_pose):
            self.determineVmax(pos, tar_pose)
            
            for i in range(len(pos)):
                if abs(pos[i] - tar_pose[i]) > self.minV * 5:
                    #there are some odd issues with the braking triggers not resetting properly
                    if abs(pos[i] - tar_pose[i]) > self.minV * 10:
                        self.braking[i] = False
                    
                    v = self.determineSpeed(pos, tar_pose, i)
                    
                    if pos[i] < tar_pose[i] and pos[i]+v < pos_max[i]: # Should fix the "looking up infinitely" bug
                        pos[i]+=v
                    elif pos[i] > tar_pose[i] and pos[i]-v > pos_min[i]:
                        pos[i]-=v
                else:
                    pos[i] = tar_pose[i]
                    self.braking[i] = False
          
            r = aI.moveTo(pos)
            if printing: print "Action: move: sent:",pos
            if printing: print "Action: move: response:",r.strip('\r\n'), "\n"
        else:
            print "Action: move: Done moving."
    
    def loopCheck(self):
        """ 
        Function to check whether the maximum amount of loops has been reached. Also delays execution of the loops if TEST_MODE_SLOW is active. 
        """
        
        #if TEST_MODE_SLOW: time.sleep(0.01)
        
        if self.loops_executed >= self.max_loops:
            self.loops_executed = 0
            return EXIT_CODE_DONE
        else:
            self.loops_executed+=1
            return 1
        
    
    def execute(self,loops = 250):
        """
        This method is intended to be overwritten by the separate Actions, but should always start with
        
        self.max_loops = loops
        if self.loopCheck() == EXIT_CODE_DONE:
            return EXIT_CODE_DONE
        
        @param loops: The amount of times the action will execute a "step" until it finishes. Defaults to 50.
        """
        self.max_loops = loops
        if self.loopCheck() == EXIT_CODE_DONE:
            return EXIT_CODE_DONE
        print self.loops_executed
        return EXIT_CODE_A1
    
    def getUserContactAngles(self):
        return Action.user_contact_angles
