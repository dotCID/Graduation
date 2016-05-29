"""
This interface reads inputs from the IMU and publishes them to the appropriate channels.
"""

## Make it possible to import from parent directory:
import sys
sys.path.insert(0,'..')

import serial, time, zmq

## Global variables
from globalVars import CHANNEL_IMU_RAWACCEL
from globalVars import CHANNEL_IMU_RAWPOS
from globalVars import IMU_ARDUINO_ADDRESS
from globalVars import IMU_ARDUINO_BAUDRATE

## Change terminal window header for easier identification of contents
sys.stdout.write("\x1b]2;Sensors/IMUInterface.py\x07")

## ZMQ setup
a_context = zmq.Context()
rawaccel = a_context.socket(zmq.PUB)
rawaccel.bind(CHANNEL_IMU_RAWACCEL)

p_context = zmq.Context()
rawpos = p_context.socket(zmq.PUB)
rawpos.bind(CHANNEL_IMU_RAWPOS)

## Set up the Arduino
imu_arduino = serial.Serial(IMU_ARDUINO_ADDRESS, IMU_ARDUINO_BAUDRATE, timeout=.1)
line = imu_arduino.readline().strip()
print "\n -- Connected to Arduino --\n"

## Function to read the imu arduino and check if the line is new
def ardRead():
    global line, imu_arduino
    newline = imu_arduino.readline().strip()
    if newline != line: 
        line = newline
    return line
    
## Arduino-style millis() function for timekeeping
millis = lambda: int(round(time.time() * 1000))

while True:    
    arduino_data = ardRead()
    
    # All accellerometer data starts with ">"
    # All position data starts with "["
    if len(arduino_data) <= 1:
        # garbage input
        time.sleep(0.02)
        continue
    elif arduino_data[0] != ">" and arduino_data[0] != "[":
        # input not relevant for computation, but is for the user
        print arduino_data
        time.sleep(0.02)
        continue
    elif arduino_data[0] == ">":
        # strip the ">"
        accel_data = arduino_data[1:]
        
        # Split the data
        acc_data = accel_data.split(",")
        
        acc_msg = {
                    't' : millis(),
                    'x' : float(acc_data[0]),
                    'y' : float(acc_data[1]),
                    'z' : float(acc_data[2])
                  }
        
        print "acc_msg = ", acc_msg, "\t",
        rawaccel.send_json(acc_msg)
        
    elif arduino_data[0] == "[":
        # strip the "["
        posit_data = arduino_data[1:]
        
        pos_data = posit_data.split(",")
        
        pos_msg = {
                    't' : millis(),
                    'x' : float(pos_data[0]),
                    'y' : float(pos_data[1]),
                    'z' : float(pos_data[2])
                  }
        
        print "pos_msg = ", pos_msg
        rawpos.send_json(pos_msg)
