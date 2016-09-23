#!/usr/bin/python
import serial, time

jointNames = ('BH', 'BV', 'TV')
currAngles = [ 94.0,  75.0,  90.0]
connected = False

def arduinoConnect(port, baudrate):
    """
    Function to connect to the Arduino
    @param str port: the port where the Arduino is to be found, f.i. '/dev/ttyACM6'
    """
    
    global arduino, connected
    if not connected:
        print "Connecting to Arduino on", port
        try:
            arduino = serial.Serial(port, baudrate, timeout=.1)
            response = ""
            while len(response) < 1: # should prevent starting the rest of the program before the Arduino is ready
                time.sleep(1)
                response = arduino.readline()
            connected = True
            return response
        except serial.serialutil.SerialException:
            print "No serial connection on ", port, "- quitting execution."
            quit() # In case this happens, don't attempt to run any more
    else:
        print "Already connected to Arduino on", port
        return ""


def arduinoWrite(val, i):
    """
    Function to write the motor commands over Serial to the Arduino and print the response(s)
    @param double val: the value to be written
    @param int i: the index number of the motor. This corresponds to the names in jointNames.
    """
    if connected:
        global arduino
        arduino.write(jointNames[i] + " "+ str(val) +"\n")
        response = arduino.readline()
        return response
    
def moveTo(joint_angles):
    """
    Sends the target joint angles to the Arduino. Returns whatever the Arduino responded with.
    @param joint_angles: An array of doubles representing angles for all joints
    """
    
    global currAngles
    totalResponse = "<"
    for i in range(len(joint_angles)):
        totalResponse += arduinoWrite(joint_angles[i], i).strip()
        totalResponse += ", "
        currAngles[i] = joint_angles[i]
    
    totalResponse += ">"
    return totalResponse

def getAngles():
    """    Simply return the currently set joint angles.    """    
    return currAngles
