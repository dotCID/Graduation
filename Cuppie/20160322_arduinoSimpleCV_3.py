#!/user/bin/python
import serial, time, math, SimpleCV

# Follow a marker with distance based accelleration

printing = True
print_response = False

dt = 0.0001

vmin = 0.01
maxV = 4.00
vmax = [maxV, maxV, maxV, maxV]
vCurr = [vmin, vmin, vmin, vmin]

arduino = None

a = 0.15

dpx = 0.0725 # approximate amount of degrees per pixel

width = 640
height = 480
display = SimpleCV.Display()
cam = SimpleCV.Camera(1, {"width":width,"height":height})

#target box for the marker
box_d = 20
yTgt = (height/2-box_d, height/2+box_d)
xTgt = (width/2-box_d, width/2+box_d)

centre = (height/2, width/2)

# position format: (joint0, joint1, joint2, joint3)
pos = [94, 155, 98, 145]
pos_default = (94, 155, 98, 145)
pos_search = (94, 125, 98, 175)
pos_search_left = (0, 125, 98, 175)
pos_search_right = (180, 125, 98, 175)
braking = [False, False, False, False]
jointNames = ('BH', 'BV', 'TH', 'TV')

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


# Calculates the stopping distance based on the velocity given
# @param double vCurr: velocity to stop from
def stoppingDistance(vCurr):
    d_stop = (-(vCurr * vCurr)) / (2.0 * -a)      # -a because we're stopping
    if printing: print "d_stop:" + str(round(d_stop,2)) +"\t",
    return d_stop


# Function to determine remaining movement distance
# @param pos:  current position
# @param goal: target position
# @return: double d_rem: distance remaining
def distanceRemaining(pos, goal):
    d_rem = abs(goal - pos)
    if printing: print "d_rem:" + str(round(d_rem,2)) +"\t",
    return d_rem


# determines the relative maximume velocities needed to finish all movement at the same time
# @param list pos: a list of current positions
# @param list goal: the target positions
def determineVmax(pos, goal):
    global vmax, maxV
    d_rem = []
    for i in range(len(pos)):
        d_rem.append(distanceRemaining(pos[i], goal[i]))
    
    i_max = d_rem.index(max(d_rem))
    if d_rem[i_max] == 0: return
    vmax[i_max] = maxV
    
    for j in range(4):
        if not j == i_max:
            vmax[j] = d_rem[j] / d_rem[i_max] / maxV


# Function to determine the speed of the joints
# @param list pos: the current joint positions
# @param list goal: the target positions
# @param i the index of the currently used point {needed for global vCurr}
def determineSpeed(pos, goal, i):
    global vCurr, vmax, vmin, a, braking
    
    if distanceRemaining(pos[i], goal[i]) < stoppingDistance(vCurr[i]):
        braking[i] = True
    
    if not braking[i]:
        if vCurr[i] < vmax[i]:
            if vCurr[i]+a > vmax[i]:
                vCurr[i] = vmax[i]
            else:
                vCurr[i]+=a
    else:
        if vCurr[i] > vmin:
            if vCurr[i]-a < vmin:
                vCurr[i] = vmin
                print "minimum speed"
            else:
                vCurr[i]-=a
                    
    if printing: print "vCurr:" + str(round(vCurr[i],2)) +"\t",
    return vCurr[i]


# Compare two lists and determine whether their contents are equal
# @param list list1: some list of arbitrary length
# @param list list2: some list of the same length
def done(list1, list2):
    if len(list1)!=len(list2): return False
    
    done_count = 0
    
    for i in range(len(list1)):
        #if list1[i] == list2[i]:
        if abs(list1[i] - list2[i]) < vmin * 3: #A bit of tolerance is needed to prevent infinite loops
            done_count+=1
            
    if done_count == len(list1):
        return True
    else:
        return False


# Function to move the current position of the motors
# @param list pos: the list of current positions
# @param list end_pose: the list of desired end poses
def move(pos, end_pose):
    global braking
    if not done(pos, end_pose):
        determineVmax(pos, end_pose)
        
        for i in range(len(pos)):
            if abs(pos[i] - end_pose[i]) > vmin * 5:
                #there are some odd issues with the braking triggers not resetting properly
                if abs(pos[i] - end_pose[i]) > vmin *10:
                    braking[i] = False
                
                v = determineSpeed(pos, end_pose, i)
                
                if pos[i] < end_pose[i]:
                    pos[i]+=v
                else:
                    pos[i]-=v
            else:
                pos[i] = end_pose[i]
                braking[i] = False
            
            arduinoWrite(pos[i], i)
        if printing: print "."

def search():
    img = cam.getImage()
    objective = img.colorDistance(color=(90,240,255)).invert()
    seg_objective = objective.stretch(220,255)
    blobs = seg_objective.findBlobs()
    
    if blobs:
        if blobs[-1].area() > 5:
            center_point = (blobs[-1].x, blobs[-1].y) #blob[-1] is the largest one
            img.drawCircle((blobs[-1].x, blobs[-1].y), 10,SimpleCV.Color.YELLOW,3)
            
            img.dl().rectangle2pts((xTgt[0], yTgt[0]), (xTgt[1],yTgt[1]), SimpleCV.Color.RED)
            img.show()
            return center_point
    img.dl().rectangle2pts((xTgt[0], yTgt[0]), (xTgt[1],yTgt[1]), SimpleCV.Color.RED)
    img.show()
    return None

def search_ball():
    img = cam.getImage()
    objective = img.colorDistance(color=(255,255,255)).invert()
    seg_objective = objective.stretch(170,235)
    blobs = seg_objective.findBlobs()
    
    if blobs:
        for blob in blobs:
            if blob.area() > 25 and blob.isCircle(0.2):
                center_point = (blob.x, blob.y) #blob[-1] is the largest one
                img.drawCircle((blob.x, blob.y), 10,SimpleCV.Color.YELLOW,3)
            
                img.dl().rectangle2pts((xTgt[0], yTgt[0]), (xTgt[1],yTgt[1]), SimpleCV.Color.RED)
                img.show()
                return center_point
    img.dl().rectangle2pts((xTgt[0], yTgt[0]), (xTgt[1],yTgt[1]), SimpleCV.Color.RED)
    img.show()
    return None

millis = lambda: int(round(time.time() * 1000))

#############################################################
#                   RUNNING CODE BELOW                      #
#############################################################

arduinoConnect('/dev/ttyACM3')

tar_x = 0
tar_y = 0
deg_x = 0
deg_y = 0
findTime = 0
t_thresh = 1500
searching = False
searchDir = 1

startTime = millis()
lastLoop = 0

while display.isNotDone():    
    #print 1000 / (millis() - lastLoop)
    #lastLoop = millis()
    #print (millis()-startTime)/1000
    
    target = search()
#    target = search_ball()
    
    if target is not None:
        searching = False
        tar_x = target[0]-width/2 
        tar_y = target[1]-height/2
        findTime = millis()
        print "Hit!"
    elif millis() - findTime > t_thresh and not searching:
        
        braking = [False, False, False, False]
        move(pos, pos_search)
        if done(pos, pos_search):
            searching = True
            print "Searching!"
        continue            
    elif searching:
        if searchDir == 1: 
            move(pos, pos_search_left)
            if done(pos, pos_search_left):
                searchDir = -1
                print "Looking left now."
        else:
            move(pos, pos_search_right)
            if done(pos, pos_search_right):
                searchDir = 1
                print "Looking right now."
        continue
                
    # Having the target within the box is acceptable
    if abs(tar_x) > box_d:
        deg_x = tar_x * dpx
    else:
        deg_x = 0
        
    if abs(tar_y) > box_d:
        deg_y = tar_y * dpx
    else:
        deg_y = 0
    
    newpos = (pos[0] + deg_x, pos[1], pos[2], pos[3] - deg_y)
        
    move(pos, newpos)
