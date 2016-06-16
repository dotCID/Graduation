#!/user/bin/python
"""
An action where the robot scans its surroundings for eye contact.
"""

import random, time
from Action import Action

## Exit codes
from globalVars import EXIT_CODE_DONE
from globalVars import EXIT_CODE_ERROR
from globalVars import EXIT_CODE_SCAN
from globalVars import EXIT_CODE_CONTACT

EXIT_CODE_SELF = EXIT_CODE_SCAN

## zmq
import zmq
from globalVars import CHANNEL_TARGETDATA
from globalVars import CHANNEL_IMU_RAWPOS

from globalVars import printing

## Poses
from poses import scan_pos_L
from poses import scan_pos_R

millis = lambda: int(round(time.time() * 1000))


class SpecificAction(Action):    
    # Target channel:
    context = zmq.Context()
    targetChannel = context.socket(zmq.SUB)
    targetChannel.setsockopt(zmq.CONFLATE, 1 )
    targetChannel.setsockopt(zmq.SUBSCRIBE, '')
    targetChannel.connect(CHANNEL_TARGETDATA)
    targetPoller = zmq.Poller()
    targetPoller.register(targetChannel, zmq.POLLIN)
    
    ## ZMQ Movement Data channel - Provides data on user position
    mv_context = zmq.Context()
    movementChannel = mv_context.socket(zmq.SUB)
    movementChannel.setsockopt(zmq.CONFLATE, 1 )
    movementChannel.setsockopt(zmq.SUBSCRIBE, '')
    movementChannel.connect(CHANNEL_IMU_RAWPOS)
    movementPoller = zmq.Poller()
    movementPoller.register(movementChannel, zmq.POLLIN)
    
    # Variables
    targetData = {
                            't'       : 0,
                            'findTime': 0,
                            'found'   : False,
                            'tar_px'  : {'x':0.0, 'y':0.0},
                            'tar_dg'  : {'x':0.0, 'y':0.0}
                        }
    findTime = 0
    deg_x = 0.0
    deg_y = 0.0
    
    movementData = {
                            't'       : 0,
                            'x'   : 180.0,
                            'y'   : 180.0,
                            'z'   : 180.0
                           }
    
    
    tried_last_loc = True
    
    def getTargetData(self):
        """ Returns either new information or the last known position of the target. """
        global targetData
        if len(self.targetPoller.poll(0)) is not 0:
            return self.targetChannel.recv_json()
        else: return self.targetData
    
    def getMovementData(self):
        """ Returns either new information or the last known user position """
        if len(self.movementPoller.poll(0)) is not 0:
            return self.movementChannel.recv_json()
        else: return self.movementData
    
    def execute(self,loops = 150):
        """
        Main executing method of this Action.
        @param loops: The amount of times the action will execute a "step" until it finishes. Defaults to 50.
        """
        global targetData
        # the general max speed is a bit high here
        self.maxV = 1.00
        
        global scan_pos_L, scan_pos_R
        
        self.max_loops = loops
        if self.loopCheck() == EXIT_CODE_DONE:
            return EXIT_CODE_DONE
            
        targetData = self.getTargetData()
        if targetData['found']:
            print "Action_Scan: Found target"
            Action.contact_joint_positions = self.currentPosition()
            movementData = self.getMovementData()
            Action.user_contact_angles = movementData
            self.tried_last_loc = False
            return EXIT_CODE_CONTACT
        elif self.done(self.currentPosition(), self.pos_target):
            if not self.tried_last_loc:
                print "trying last location"
                print targetData['tar_px']
                if targetData['tar_px']['x'] > 0:
                    self.pos_target = scan_pos_R
                    print "Target was to my right"
                elif targetData['tar_px']['x']<0:
                    self.pos_target = scan_pos_L
                    print "Target was to my left"
                self.tried_last_loc = True
            if self.done(self.pos_target, Action.contact_joint_positions):
                rd = random.random()
                if rd > 0.5:
                    self.pos_target = scan_pos_L
                else:
                    self.pos_target = scan_pos_R
            elif self.done(self.pos_target, scan_pos_L):
                self.pos_target = scan_pos_R
            elif self.done(self.pos_target, scan_pos_R):
                self.pos_target = scan_pos_L
            else:
                self.pos_target = scan_pos_L #this is the case if no target has been set other than default, for instance.
        self.move(self.pos_target)
        
        return EXIT_CODE_SELF
