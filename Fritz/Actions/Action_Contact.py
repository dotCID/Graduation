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
from globalVars import EXIT_CODE_ACK

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
import time
from globalVars import printing
from globalVars import THRESHOLD_EDIFF
from globalVars import ENERGY_CALC_TIME
from globalVars import BPM_DIFF

from poses import contact_joint_positions

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
        return self.beatDataChannel.recv_json()['s0_avg']
        
    def getBeatData(self):
        """ Simple function for shorter syntax """
        '''if len(self.beatDataPoller.poll(0)) is not 0:
            return self.beatDataChannel.recv_json()
        else:
            return self.beatData
        '''
        #above would output so many 0's that it skewed results, better to use blocking than a poller
        return self.beatDataChannel.recv_json()
            
    def setBPM(self, newBPM):
        """ Sets the BPM in Ableton """
        client = OSCClient()
        client.connect((OSC_ABLETON_IP, 9000))
        msg = OSCMessage()
        msg.setAddress("/live/tempo")
        msg.append(newBPM)
        client.send(msg)
        if printing: print "Set BPM to",newBPM
        self.currBPM = newBPM
        Action.BPM = self.currBPM # change the head bob bpm as well
            
    def adjustBPM(self):
        """ Adjust the BPM in Ableton according to the measured values """
        ediff = self.averageEnergy - self.localAvgEnergy
        print "Average long energy: ",self.averageEnergy, " Short term:",self.localAvgEnergy
        print "ediff was", ediff
        
        bpmDifference = abs(round(ediff/10,0)*10)
        
        if bpmDifference > BPM_DIFF:
            bpmDifference = BPM_DIFF
        
        if abs(ediff) > THRESHOLD_EDIFF:
            oldBPM = self.getBPM(self.currBPM)
            newBPM = oldBPM
            if ediff < 0:
                newBPM = oldBPM + bpmDifference
                self.pedalResponse("up") # Communicate to Action that a response should be given
            else:
                newBPM = oldBPM - bpmDifference
                self.pedalResponse("down") # Communicate to Action that a response should be given
            print "newBPM: ",newBPM

            self.setBPM(newBPM)
                
            
    def execute(self,loops = 500):
        """
        Main executing method of this Action.
        @param loops: The amount of times the action will execute a "step" until it finishes. Defaults to 50.
        """
        # Not relevant for this Action
        #self.max_loops = loops
        #if self.loopCheck() == EXIT_CODE_DONE:
        #    return EXIT_CODE_DONE
        
        if not self.done(self.currentPosition(), contact_joint_positions):
            if printing: print "Action_Contact: Moving to look at pedal user"
            self.move(contact_joint_positions)
            return EXIT_CODE_SELF
        else:
            if self.averageEnergy is None:
                self.averageEnergy = self.getEnergyAvg()
            else:
                # calculate BPM over given interval
                if self.energy_calc_start is None:
                    self.energy_calc_start = self.millis()
                    
                if (self.millis() - self.energy_calc_start) < (ENERGY_CALC_TIME-1) * 1000:
                    self.energyVals.append(self.getBeatData()['s0'])
                    print "calculating energy (",self.millis() - self.energy_calc_start, ")"
                else:
                    self.localAvgEnergy = sum(self.energyVals)/len(self.energyVals)
                    self.adjustBPM()
                    
                    # clear old values
                    self.energyVals = []
                    self.energy_calc_start = None
                    self.averageEnergy = None
                    
                    return EXIT_CODE_ACK
            
            return EXIT_CODE_SELF
