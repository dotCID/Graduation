#!/user/bin/python
"""
Specific Action Class for maintaining eye contact with user and adjusting beat when the data indicates it should be
"""
from Action import Action
import arduinoInterface as aI 

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
from globalVars import CHANNEL_ACCELDATA
from globalVars import CHANNEL_BPM
from globalVars import CHANNEL_BEAT

## OSC
from OSC import OSCClient
from OSC import OSCMessage
from globalVars import OSC_ABLETON_IP

## Other
import time
from globalVars import printing
from globalVars import THRESHOLD_EDIFF
from globalVars import ENERGY_CALC_MEASURES
from globalVars import BPM_SHIFT_WAIT_MEASURES
from globalVars import BPM_SHIFT_CNTDWN_MEASURES
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

    # Accel Data channel:
    accelDataChannel = context.socket(zmq.SUB)
    accelDataChannel.setsockopt(zmq.CONFLATE, 1 )
    accelDataChannel.setsockopt(zmq.SUBSCRIBE, '')
    accelDataChannel.connect(CHANNEL_ACCELDATA)
    accelDataPoller = zmq.Poller()
    accelDataPoller.register(accelDataChannel, zmq.POLLIN)

    # BPM channel:
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
    startBeat = None
    energy_calc_start = None
    energyVals = []
    accelData = {
                   't'           : 0,
                   'a_avg_short' : 0.0,
                   'a_avg_long'  : 0.0
                }
          
    currBPM = 120.0
    BPMAdjustment = 0
    adjustmentConfirmed = False
    countDownAnimStarted = False
    
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
        return self.accelDataChannel.recv_json()['a_avg_long']
        
    def getAccelData(self):
        return self.accelDataChannel.recv_json()
        
            
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
        
        aI.setBPM(newBPM)         # Change the lighting BPM too
            
    def calcAdjustBPM(self):
        """ Calculate the BPM adjustment """
        ediff = self.averageEnergy - self.localAvgEnergy
        print "Average long energy: ",self.averageEnergy, " Short term:",self.localAvgEnergy
        print "ediff was", ediff
        
        if abs(ediff) > THRESHOLD_EDIFF:
            if ediff < 0:
                print "negative eDiff"
                return BPM_DIFF
            else:
                print "positive eDiff"
                return BPM_DIFF * -1

        print "Difference was too small."
        return 0
        
                
            
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
            self.moveQuick(contact_joint_positions)
            return EXIT_CODE_SELF
        
        if self.averageEnergy is None:
            if printing: print "Getting energy average"
            self.averageEnergy = self.getEnergyAvg()
        else:
            # calculate BPM over given interval
            
            # but only from the start of a measure, assuming 4/4 timing
            if self.startBeat is None:
                self.startBeat = self.getBeat()
            
            if self.startBeat%4!=0 and self.energy_calc_start is None:
                print "Waiting for measure to start",self.startBeat
                self.startBeat = None
                return EXIT_CODE_SELF
            else:                    
                if self.energy_calc_start is None:
                    self.energy_calc_start = self.millis()
                
                beat = self.getBeat()
                
                # Append energy when the required amount of beats has not been reached yet
                if (beat / 4.0) - (self.startBeat / 4.0) <= ENERGY_CALC_MEASURES:
                    # Turn on the LEDs constantly to indicate listening
                    aI.pixOn()
                    self.energyVals.append(self.getAccelData()['a_avg_short'])
                    print "calculating energy (",self.millis() - self.energy_calc_start, ")", beat
                
                # Then confirm
                elif (beat / 4.0) - (self.startBeat / 4.0) <= ENERGY_CALC_MEASURES + BPM_SHIFT_WAIT_MEASURES:
                    if not self.adjustmentConfirmed:
                        self.localAvgEnergy = sum(self.energyVals)/len(self.energyVals)
                        self.BPMAdjustment = self.calcAdjustBPM()
                        
                        # BPM up/down animation  
                        if self.BPMAdjustment > 0.0:
                            print "BPM will go up", self.BPMAdjustment
                            self.pedalResponse("up") # Communicate to Action that a response should be given
                            aI.bpmUp()
                        elif self.BPMAdjustment < 0.0:
                            print "BPM will go down", self.BPMAdjustment
                            self.pedalResponse("down") # Communicate to Action that a response should be given
                            aI.bpmDown()
                        else:
                            print "BPM stays unchanged", self.BPMAdjustment
                            aI.bpmSame()
                        self.adjustmentConfirmed = True
                        
                # Count down
                elif not self.countDownAnimStarted:
                    self.currBPM = self.getBPM(self.currBPM)
                
                    # BPM countdown animation           
                    LEDDelay = 60000.0 / self.currBPM
                    

                    if self.BPMAdjustment > 0:                        
                        print "Starting countup animation", LEDDelay, beat
                        aI.bpmCountUp(LEDDelay)
                    elif self.BPMAdjustment < 0:
                        print "Starting countdown animation", LEDDelay, beat
                        aI.bpmCountDown(LEDDelay)
                        
                    self.countDownAnimStarted = True
                # Adjust BPM
                if (beat / 4.0) - (self.startBeat / 4.0) >= ENERGY_CALC_MEASURES + BPM_SHIFT_WAIT_MEASURES + BPM_SHIFT_CNTDWN_MEASURES:
                    print "Applying adjustment.", beat
                    self.setBPM(self.currBPM + self.BPMAdjustment)
                    
                    # clear old values
                    self.adjustmentConfirmed = False
                    self.countDownAnimStarted = False
                    self.energyVals = []
                    self.energy_calc_start = None
                    self.averageEnergy = None
                    self.startBeat = None
                    aI.ready()  #resets pixel pattern
                    
                    return EXIT_CODE_ACK
            
        return EXIT_CODE_SELF
