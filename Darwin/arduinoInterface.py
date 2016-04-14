#!/usr/bin/python
import serial, time

jointNames = ('BH', 'BV', 'TH', 'TV')

# Function to connect to the Arduino
# @param str port: the port where the Arduino is to be found, f.i. '/dev/ttyACM6'
def arduinoConnect(port, baudrate):
    global arduino
    print "connecting"
    arduino = serial.Serial(port, baudrate, timeout=.1)
    time.sleep(1)
    response = arduino.readline()
    return response


# Function to write the motor commands over Serial to the Arduino and print the response(s)
# @param double val: the value to be written
# @param int i: the index number of the motor. This corresponds to the names in jointNames.
def arduinoWrite(val, i):
    global arduino
    arduino.write(jointNames[i] + " "+ str(val) +"\n")
    response = arduino.readline()
    return response
