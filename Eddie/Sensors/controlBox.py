'''
This script replaces the energy measurement and head bob BPM detection by inputs from an external control box.
'''

# make it possible to import from parent directory:
import sys
sys.path.insert(0,'..')

from globalVars import CONTROLBOX_ARDUINO_ADDRESS
from globalVars import CONTROLBOX_ARDUINO_BAUDRATE
from globalVars import CHANNEL_ENERGYDATA
from globalVars import CHANNEL_BPM

import serial, time
import zmq

## Change terminal window header for easier identification of contents
sys.stdout.write("\x1b]2;Sensors/controlBox.py\x07")


## Arduino setup
box_arduino = serial.Serial(CONTROLBOX_ARDUINO_ADDRESS, CONTROLBOX_ARDUINO_BAUDRATE, timeout=.1)
line = box_arduino.readline().strip()
print "controlbox: \n", line

## ZMQ EnergyData channel
energy_context = zmq.Context()
energy_socket = energy_context.socket(zmq.PUB)
energy_socket.bind(CHANNEL_ENERGYDATA)

## ZMQ BPM channel
bpm_context = zmq.Context()
bpm_socket = bpm_context.socket(zmq.PUB)
bpm_socket.bind(CHANNEL_BPM)

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
    
        eg_msg = {
                    't'        : millis(),
                    'energy'   : 0.0,
                    'eg_label' : data[1]
                 }
        bpm_msg = {
                    't':millis(),
                    'bpm':data[0]
                  }
    
        print "Control Box: ",arduino_data
                  
        energy_socket.send_json(eg_msg)
        bpm_socket.send_json(bpm_msg)
