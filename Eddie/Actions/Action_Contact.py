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
    findTime = 0
    deg_x = 0.0
    deg_y = 0.0
    
    def getTargetData():
        """ Simple function for shorter syntax """
        if len(targetPoller.poll(0)) is not 0:
            return targetChannel.recv_json()
        else: return targetData_default
            
    def execute(self,loops = 50):
        """
        Main executing method of this Action.
        @param loops: The amount of times the action will execute a "step" until it finishes. Defaults to 50.
        """
        self.max_loops = loops
        if self.loopCheck() == EXIT_CODE_DONE:
            return EXIT_CODE_DONE
        
        targetData = getTargetData()
        if targetData['found']:
            if printing: print "Action_Contact: Found target. Following."
            deg_x = targetData['tar_dg']['x'] 
            deg_y = targetData['tar_dg']['y']
            findTime = targetData['findTime']
            pos = currentPosition()
            newpos = (pos[0] + deg_x, pos[1] - deg_y/2, pos[2] - deg_y)
            move(newpos)
            return EXIT_CODE_SELF
            
        elif not done(currentPosition(), Action.contact_joint_positions):
            if printing: print "Action_Contact: Moving to last known contact position"
            move(Action.contact_joint_positions)
            return EXIT_CODE_SELF
            
        else:
            if printing: print "Action_Contact: Target lost, scanning"
            return EXIT_CODE_SCAN
            
        return EXIT_CODE_SELF
