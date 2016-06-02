#!/user/bin/python
'''
This script replaces the energy measurement and head bob BPM detection by inputs from an external control box.
'''

# make it possible to import from parent directory:
import sys
sys.path.insert(0,'..')

from globalVars import CONTROLBOX_ARDUINO_ADDRESS
from globalVars import CONTROLBOX_ARDUINO_BAUDRATE

from Actions import Action_Scan
from Actions import Action_Focus
from Actions import Action_Bored

import serial, time
import zmq

## Actions
scan        = Action_Scan.SpecificAction()
focus       = Action_Focus.SpecificAction()
bored       = Action_Bored.SpecificAction()


## Change terminal window header for easier identification of contents
sys.stdout.write("\x1b]2;Sensors/controlBox_backupMode.py\x07")

## Arduino setup
box_arduino = serial.Serial(CONTROLBOX_ARDUINO_ADDRESS, CONTROLBOX_ARDUINO_BAUDRATE, timeout=.1)
line = box_arduino.readline().strip()
print "controlbox: \n", line

def ardRead():
    """ Function to read the imu arduino and check if the line is new """ 
    # TODO: move this to the interface?
    global line, box_arduino
    newline = box_arduino.readline().strip()
    if newline != line: 
        line = newline
    return line
    
# MCW: Arduino-style millis() function for timekeeping
millis = lambda: int(round(time.time() * 1000))

while True:
    arduino_data = ardRead()
    
    if len(arduino_data) <= 5:
        # garbage input
        time.sleep(0.02)
        continue
    else:
        data = arduino_data.split(", ")
    
        knob_state = data[1]
        
        if knob_state == "none":
            scan.execute(150)
            print "Scanning"
        elif knob_state == "low":
            focus.execute(150)
            print "Focusing"
        elif knob_state == "high":
            bored.execute(150)
            print "Bored."
        
        print arduino_data
