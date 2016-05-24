#!/user/bin/python
"""
Specific Action Class for maintaining eye contact with user.
"""

#TODO: check whether usage of global braking, etc, varaiables causes bugs.


from Action import Action

## Exit codes
from globalVars import EXIT_CODE_DONE
from globalVars import EXIT_CODE_ERROR
from globalVars import EXIT_CODE_SCAN
from globalVars import EXIT_CODE_CONTACT

EXIT_CODE_SELF = EXIT_CODE_CONTACT

## zmq
import zmq
from globalVars import CHANNEL_TARGETDATA

from globalVars import printing

class SpecificAction(Action):

    # Target channel:
    context = zmq.Context()
    targetChannel = context.socket(zmq.SUB)
    targetChannel.setsockopt(zmq.CONFLATE, 1 )
    targetChannel.setsockopt(zmq.SUBSCRIBE, '')
    targetChannel.connect(CHANNEL_TARGETDATA)
    targetPoller = zmq.Poller()
    targetPoller.register(targetChannel, zmq.POLLIN)
    
    # Variables
    targetData_default = {
                            't'       : 0,
                            'findTime': 0,
                            'found'   : False,
                            'tar_px'  : {'x':0.0, 'y':0.0},
                            'tar_dg'  : {'x':0.0, 'y':0.0}
                        }
    targetData = targetData_default
    findTime = 0
    deg_x = 0.0
    deg_y = 0.0
      
    
    def getTargetData(self):
        """ Simple function for shorter syntax """
        if len(self.targetPoller.poll(0)) is not 0:
            return self.targetChannel.recv_json()
        else:
            return self.targetData
            
    def execute(self,loops = 500):
        """
        Main executing method of this Action.
        @param loops: The amount of times the action will execute a "step" until it finishes. Defaults to 50.
        """
        self.max_loops = loops
        if self.loopCheck() == EXIT_CODE_DONE:
            return EXIT_CODE_DONE
        
        self.targetData = self.getTargetData()
        if self.targetData['found']:
            if printing: print "Action_Contact: Found target. Following."
            deg_x = self.targetData['tar_dg']['x'] 
            deg_y = self.targetData['tar_dg']['y']
            findTime = self.targetData['findTime']
            
            print "Action_Contact: adjustment: ", deg_x, deg_y
            
            pos = self.currentPosition()
            newpos = (pos[0] + deg_x, pos[1], pos[2] + deg_y)
            self.move(newpos)
            return EXIT_CODE_SELF
            
        elif not self.done(self.currentPosition(), Action.contact_joint_positions):
            if printing: print "Action_Contact: Moving to last known contact position"
            self.move(Action.contact_joint_positions)
            return EXIT_CODE_SELF
            
        else:
            if printing: print "Action_Contact: Target lost, scanning"
            return EXIT_CODE_SCAN
            
        return EXIT_CODE_SELF
