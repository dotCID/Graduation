#!/user/bin/python
import serial, time, math

#move from one pose to another based on accelleration

printing = False
print_response = False

dt = 0.0001

vmin = 0.03
maxV = 4.00
vmax = [maxV, maxV, maxV, maxV]
vCurr = [vmin, vmin, vmin, vmin]

arduino = None

a = 0.15

# position format: (joint0, joint1, joint2, joint3)
pos = [94, 155, 98, 145]
braking = [False, False, False, False]
jointNames = ('BH', 'BV', 'TH', 'TV')

pose_1 = (140, 120, 98, 180)
pose_2 = (50, 120, 98, 180)
pose_3 = (130, 120, 98, 180)
pose_4 = (94, 155, 98, 145)

pose_5 = (94, 135, 98, 165)
pose_6 = (94, 120, 98, 180)


head_1 = (94, 155, 98, 135)
head_2 = (94, 155, 98, 160)

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
def distanceRemaining(pos, goal):
    d_rem = abs(goal - pos)
    if printing: print "d_rem:" + str(round(d_rem,2)) +"\t",
    return d_rem


# determines the relative maximume velocities needed to finish all movement at the same time
# @param list pos: a list of current positions
# @param list goal: the target positions
def determineVmax(pos, goal):
    global vmax, maxV
    d_rem = [distanceRemaining(pos[0], goal[0]), \
             distanceRemaining(pos[1], goal[1]), \
             distanceRemaining(pos[2], goal[2]), \
             distanceRemaining(pos[3], goal[3])]
    
    i_max = d_rem.index(max(d_rem))
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
        if list1[i] == list2[i]:
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
    while not done(pos, end_pose):
        determineVmax(pos, end_pose)
        
        for i in range(len(pos)):
            if abs(pos[i] - end_pose[i]) > vmin * 3:
                
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
        print braking, vCurr
        time.sleep(dt)
    
    #below is needed in some cases, maybe TODO: investigate?
    braking = [False, False, False, False]


#############################################################
#                   RUNNING CODE BELOW                      #
#############################################################

arduinoConnect('/dev/ttyACM3')
'''
print "pose 1:"
move(pos, pose_1)
time.sleep(0.5)
print "pose 2:"
move(pos, pose_2)
time.sleep(0.5)

print "pose 3:"
move(pos, pose_3)
time.sleep(0.5)

print "pose 4:" 
move(pos, pose_4)
'''
'''
print "head cycle:"
a /= 4
for i in range(6):
    move(pos, head_1)
    move(pos, head_2)
print "done."
'''
a = 0.07
print "pose 5:" 
move(pos, pose_5)
time.sleep(1)
move(pos, pose_4)

a = 0.3
time.sleep(2)
move(pos, pose_6)
time.sleep(1)
move(pos, pose_4)
time.sleep(10)
