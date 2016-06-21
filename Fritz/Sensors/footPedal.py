#!/user/bin/python
"""
Outputs the current state of the foot pedal to a ZMQ channel.
"""

# Make it possible to import from parent directory
import sys
sys.path.insert(0,'..')

# Change terminal window header for easier identification of contents
sys.stdout.write("\x1b]2;Sensors/footPedal.py\x07")

from globalVars import PEDAL_ARDUINO_ADDRESS
from globalVars import PEDAL_ARDUINO_BAUDRATE
from globalVars import CHANNEL_PEDAL

import serial, time
import zmq

line = None
ped_arduino = None

## Arduino setup
try:
    print "Connecting to ", PEDAL_ARDUINO_ADDRESS
    ped_arduino = serial.Serial(PEDAL_ARDUINO_ADDRESS, PEDAL_ARDUINO_BAUDRATE, timeout=.1)
    line = ped_arduino.readline().strip()
    print "PEDAL: \n", line
except:
    print "Could not connect. Looping forever."
    while True:
        a = 1

## ZMQ pedal channel
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind(CHANNEL_PEDAL)

def ardRead():
    """ Function to read the imu arduino and check if the line is new """ 
    global line, ped_arduino
    newline = ped_arduino.readline().strip()
    if newline != line: 
        line = newline
    return line
    
# MCW: Arduino-style millis() function for timekeeping
millis = lambda: int(round(time.time() * 1000))

while True:
    arduino_data = ardRead()
    
    if len(arduino_data) <= 1:
        # garbage input
        time.sleep(0.02)
        continue
    else:
        data = arduino_data.split(" ")
    
        ped_msg = {
                    'state' : int(data[1])
                 }
    
        print "Pedal: ",arduino_data,
        
        print "\t Sent: ",ped_msg
                  
        socket.send_json(ped_msg)
