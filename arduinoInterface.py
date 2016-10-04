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
        response = arduino.readline()   # causes the movement to be rather slow, cause unknown
        return response
    
def moveTo(joint_angles):
    """
    Sends the target joint angles to the Arduino. Returns whatever the Arduino responded with.
    @param joint_angles: An array of doubles representing angles for all joints
    """
    
    global currAngles
    totalResponse = "<"
    for i in range(len(joint_angles)):
        # The servos are powered by a PWM signal that gives about a 0.5 degree resolution.
        # To smooth out movement, we round that out here.
        angle = round(joint_angles[i]*4.0)/4.0
        totalResponse += arduinoWrite(angle, i).strip()
        totalResponse += ", "
        currAngles[i] = angle
    
    totalResponse += ">"
    return totalResponse

def getAngles():
    """    Simply return the currently set joint angles.    """    
    return currAngles

    
def bpmSame():
    """ Activates the "bpm will not change" animation """
    arduino.write("bpmSame\n")
    
def bpmUp():
    """ Activates the "bpm will go up" animation """
    arduino.write("bpmUp\n")
    
def bpmDown():    
    """ Activates the "bpm will go down" animation """
    arduino.write("bpmDown\n")

def bpmCountUp(delay):
    """ 
    Activates the "bpm will go up in .. " animation
    @param int delay: determines the time between LEDs lighting
    """
    arduino.write("bpmAnimUp "+str(delay)+"\n")

def bpmCountDown(delay):
    """ 
    Activates the "bpm will go down in .. " animation
    @param int delay: determines the time between LEDs lighting
    """
    arduino.write("bpmAnimDown "+str(delay)+"\n")

def ready():
    """
    Signals the bot that the PC is ready
    """
    arduino.write("start\n")

