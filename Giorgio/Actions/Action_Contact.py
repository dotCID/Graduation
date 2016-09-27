#!/user/bin/python
"""
Specific Action Class for maintaining eye contact with user and adjusting beat when the data indicates it should be
"""
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
from globalVars import CHANNEL_BEATDATA
from globalVars import CHANNEL_BPM

## OSC
from OSC import OSCClient
from OSC import OSCMessage
from globalVars import OSC_ABLETON_IP

## Other
from globalVars import printing
from globalVars import THRESHOLD_EDIFF
from globalVars import ENERGY_CALC_TIME
from globalVars import BPM_DIFF

class SpecificAction(Action):

    # Target channel:
    context = zmq.Context()
    targetChannel = context.socket(zmq.SUB)
    targetChannel.setsockopt(zmq.CONFLATE, 1 )
    targetChannel.setsockopt(zmq.SUBSCRIBE, '')
    targetChannel.connect(CHANNEL_TARGETDATA)
    targetPoller = zmq.Poller()
    targetPoller.register(targetChannel, zmq.POLLIN)

    # Beat Data channel:
    context = zmq.Context()
    beatDataChannel = context.socket(zmq.SUB)
    beatDataChannel.setsockopt(zmq.CONFLATE, 1 )
    beatDataChannel.setsockopt(zmq.SUBSCRIBE, '')
    beatDataChannel.connect(CHANNEL_BEATDATA)
    beatDataPoller = zmq.Poller()
    beatDataPoller.register(beatDataChannel, zmq.POLLIN)

    # BPM channel:
    context = zmq.Context()
    bpmChannel = context.socket(zmq.SUB)
    bpmChannel.setsockopt(zmq.CONFLATE, 1 )
    bpmChannel.setsockopt(zmq.SUBSCRIBE, '')
    bpmChannel.connect(CHANNEL_BPM)
    bpmPoller = zmq.Poller()
    bpmPoller.register(bpmChannel, zmq.POLLIN)
   
    # Variables
    targetData_default = {
                            't'       : 0,
                            'findTime': 0,
                            'found'   : False,
                            'tar_px'  : {'x':0.0, 'y':0.0},
                            'tar_dg'  : {'x':0.0, 'y':0.0}
                        }
    targetData = targetData_default
    
    averageEnergy = None
    localAvgEnergy = 0.0
    energy_calc_start = None
    energy_calc_finished = False
    energyVals = []
    beatData = {
                't'     : 0,
                'f0'    : 0.0,
                's0'    : 0.0,
                'avg_s0': 0.0,
                'bpm'   : 0.0,
                'beat'  : False
               }
    currBPM = 120.0
    
    findTime = 0
    deg_x = 0.0
    deg_y = 0.0
      
    
    def getTargetData(self):
        """ Simple function for shorter syntax """
        if len(self.targetPoller.poll(0)) is not 0:
            return self.targetChannel.recv_json()
        else:
            return self.targetData
    
    def getEnergyAvg(self):
        """ Simple function for shorter syntax """
        if len(self.beatDataPoller.poll(0)) is not 0:
            return self.beatDataChannel.recv_json()['s0_avg']
        else:
            return self.averageEnergy
    
    def getBeatData(self):
        """ Simple function for shorter syntax """
        if len(self.beatDataPoller.poll(0)) is not 0:
            self.beatData = self.beatDataChannel.recv_json()
        return self.beatData
    
    def getBPM(self):
        """ Simple function for shorter syntax, gets last known BPM"""
        client = OSCClient()
        client.connect((OSC_ABLETON_IP, 9000))
        msg = OSCMessage()
        msg.setAddress("/live/tempo")
        client.send(msg)
        return self.bpmChannel.recv_json()['bpm']
            
    def setBPM(self, oldBPM, newBPM):
        """ Sets the BPM in Ableton """
        client = OSCClient()
        client.connect((OSC_ABLETON_IP, 9000))
        msg = OSCMessage()
        msg.setAddress("/live/tempo")
        msg.append(newBPM)
        client.send(msg)
        if printing: print "Set BPM from ",oldBPM,"to",newBPM
            
    def adjustBPM(self):
        """ Adjust the BPM in Ableton according to the measured values """
        ediff = self.averageEnergy - self.localAvgEnergy
        
        if abs(ediff) > THRESHOLD_EDIFF:
            oldBPM = self.getBPM()
            newBPM = oldBPM
            if ediff < 0:
                newBPM = oldBPM + BPM_DIFF
            else:
                newBPM = oldBPM - BPM_DIFF
            self.setBPM(oldBPM, newBPM)
            print "BPM change made; ediff was", ediff, " (Threshold: ",THRESHOLD_EDIFF,")"
        else:
            print "No BPM change made; ediff was", ediff, " (Threshold: ",THRESHOLD_EDIFF,")"
        #reset the responsible variables
        self.energyVals = []
                

    def execute_reset(self):      
        """
        In case of a footpedal interrupt, resets all values and executes normal loop
        """            
        self.energy_calc_start = None
        self.energyVals = []
        self. energy_calc_finished = False
        
        return self.execute()
        
    def execute(self,loops = 500):
        """
        Main executing method of this Action.
        @param loops: The amount of times the action will execute a "step" until it finishes. Defaults to 50.
        """
        # Not relevant for this Action
        #self.max_loops = loops
        #if self.loopCheck() == EXIT_CODE_DONE:
        #    return EXIT_CODE_DONE
        
        # calculate BPM over given interval
        if self.energy_calc_start is None:
            print "Starting energy calculation"
            
            self.averageEnergy = self.getEnergyAvg()
            print "Average long term Energy is ",self.averageEnergy
            self.energy_calc_start = Action.millis(self)
            
        if not self.energy_calc_finished and Action.millis(self) - self.energy_calc_start < ENERGY_CALC_TIME * 1000:
            self.energyVals.append(self.getBeatData()['s0'])
        elif not self.energy_calc_finished:
            self.localAvgEnergy = sum(self.energyVals)/len(self.energyVals)
            print "\nEnergy calculation complete.", self.localAvgEnergy
            self.energy_calc_finished = True
            self.adjustBPM()
            
        self.targetData = self.getTargetData()
        if self.targetData['found']:
            if printing: print "Action_Contact: Found target. Following."
            deg_x = -self.targetData['tar_dg']['x'] 
            deg_y = -self.targetData['tar_dg']['y']
            findTime = self.targetData['findTime']
            
            print "Action_Contact: adjustment: ", deg_x, deg_y
            
            pos = self.currentPosition()
            newpos = (pos[0] + deg_x, pos[1], pos[2] + deg_y)
            self.move(newpos)
            return EXIT_CODE_SELF
            
        elif not self.done(self.currentPosition(), Action.contact_joint_positions):
           # if printing: print "Action_Contact: Moving to last known contact position"
            self.move(Action.contact_joint_positions)
            return EXIT_CODE_SELF
            
        elif not self.energy_calc_finished:
            return EXIT_CODE_SELF
        else:
            if printing: print "Action_Contact: Target lost, scanning"
            # Only reset this when done
            self.energy_calc_start = None
            self.energy_calc_finished = False
            return EXIT_CODE_SCAN
            
        return EXIT_CODE_SELF
