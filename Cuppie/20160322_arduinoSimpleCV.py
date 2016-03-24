#!/user/bin/python
import serial, time, math, SimpleCV

#Find the marker

printing = False
print_response = False

dt = 0.0001

vmin = 1
maxV = 4.00
vmax = [maxV, maxV, maxV, maxV]
vCurr = [vmin, vmin, vmin, vmin]

arduino = None

a = 0.15

# position format: (joint0, joint1, joint2, joint3)
pos = [94, 155, 98, 145]
jointNames = ('BH', 'BV', 'TH', 'TV')
jointDir = [1,1,1,1]

display = SimpleCV.Display()
cam = SimpleCV.Camera(1, {"width":640,"height":480})

# Function to connect to the Arduino
# @param str port: the port where the Arduino is to be found, f.i. '/dev/ttyACM6'
def arduinoConnect(port):
    global arduino
    print "connecting"
    arduino = serial.Serial(port, 115200, timeout=.1)
    time.sleep(1)
    response = arduino.readline()
    if print_response: print response


# Function to write the motor commands over Serial to the Arduino and print the response(s)
# @param double val: the value to be written
# @param int i: the index number of the motor. This corresponds to the names in jointNames.
def arduinoWrite(val, i):
    global arduino
    arduino.write(jointNames[i] + " "+ str(val) +"\n")
    response = arduino.readline()
    if print_response: print response



# Compare two lists and determine whether their contents are equal
# @param list list1: some list of arbitrary length
# @param list list2: some list of the same length
def done(list1, list2):
    if len(list1)!=len(list2): return False
    
    done_count = 0
    
    for i in range(len(list1)):
        if list1[i] == list2[i]:
            done_count+=1
            
    if done_count == len(list1):
        return True
    else:
        return False


def look():
    img = cam.getImage()
    objective = img.colorDistance(color=(100,235,235)).dilate(2)
    seg_objective = objective.stretch(0,50).invert()
    blobs = seg_objective.findBlobs()
    
    if blobs:
        if blobs[-1].area() > 5:
            circlelayer = SimpleCV.DrawingLayer((img.width, img.height))
            center_point = (blobs[-1].x, blobs[-1].y) #blob[-1] is the largest one
            img.drawCircle((blobs[-1].x, blobs[-1].y), 10,SimpleCV.Color.YELLOW,3)
            
            img.show()
            return True
    img.show()
    return False
    
    
# Function to move the current position of the motors
# @param list pos: the list of current positions
# @param list end_pose: the list of desired end poses
def move(pos):
     while not look():
        pos[0] += jointDir[0] * vCurr[0]
        if pos[0] == 180 or pos[0] == 0:
            jointDir[0] *= -1
        
        arduinoWrite(pos[0], 0)
        time.sleep(dt)
    

#############################################################
#                   RUNNING CODE BELOW                      #
#############################################################

arduinoConnect('/dev/ttyACM3')
move(pos)
