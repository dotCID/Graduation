#!/user/bin/python
'''
This script uses SimpleCV to grab an image from the camera and numpy to find an infrared LED and report its position relative to the camera view centre and whether it is inside the target area.

Attempted stabilisation of the output by tracking a circular object instead and altering exposure of the camera.
'''

# make it possible to import from parent directory:
import sys
sys.path.insert(0,'..')

## Change terminal window header for easier identification of contents
sys.stdout.write("\x1b]2;Sensors/simpleCV_3.py\x07")


import time, math, SimpleCV
import zmq, json
import subprocess as sp
from globalVars import CHANNEL_TARGETDATA
from globalVars import CAMERA_ID_NUMBER

printing = True

dpx = 0.0025 # approximate amount of degrees per pixel for Trust eLight

width = 960
height = 540
camera_id = 'video' + str(CAMERA_ID_NUMBER)

# To increase framerate, count the search() loops and render every n frames
renderFrame = 1
frame = 0

# Adjust camera settings from OS, since SimpleCV's commands don't do anything:
sp.call(["uvcdynctrl -d '"+camera_id+"' -s 'Exposure, Auto' 1"], shell = True)         # Disable auto exposure
sp.call(["uvcdynctrl -d '"+camera_id+"' -s 'Exposure (Absolute)' 12"], shell = True)    # Set absolute exposure

display = SimpleCV.Display()
cam = SimpleCV.Camera(CAMERA_ID_NUMBER, {"width":width,"height":height})

#target box for the marker
box_d = 20
yTgt = (height/2-box_d, height/2+box_d)
xTgt = (width/2-box_d, width/2+box_d)
box_clr = SimpleCV.Color.RED

centre = (height/2, width/2)


context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind(CHANNEL_TARGETDATA)



def search():
    global frame, renderFrame
    img = cam.getImage()
    objective = img.colorDistance(color=(255,255,255)).invert()
    seg_objective = objective.stretch(200,255)
    blobs = seg_objective.findBlobs()
    
    if blobs:
        center_point = (blobs[-1].x, blobs[-1].y)
        
        if frame is renderFrame:
            img.drawCircle((blobs[-1].x, blobs[-1].y), 10,SimpleCV.Color.YELLOW,3)
            img.dl().rectangle2pts((xTgt[0], yTgt[0]), (xTgt[1],yTgt[1]), box_clr)
            img.show()
            frame = 0
        
        frame +=1
        return center_point
  
    if frame is renderFrame:
        img.dl().rectangle2pts((xTgt[0], yTgt[0]), (xTgt[1],yTgt[1]), box_clr)
        img.show()
        frame = 0
   
    frame +=1
    return None

#get current time in milliseconds
millis = lambda: int(round(time.time() * 1000))

#############################################################
#                   RUNNING CODE BELOW                      #
#############################################################

tar_x = 0
tar_y = 0
deg_x = 0
deg_y = 0
last_tar = tar_x
found = False
findTime = 0
lastFound = findTime
lossReported = False

while display.isNotDone():
    target = search()
    
    if target is not None:
        tar_x = target[0]-width/2 
        tar_y = target[1]-height/2
        findTime = millis()
        found = True
        lossReported = False
    else:
        found = False
        lastFound = findTime
    # Angular difference between the box and the target
    # Having the target within the box is acceptable
    if abs(tar_x) > box_d:
        deg_x = tar_x * dpx
    else:
        deg_x = 0
        
    if abs(tar_y) > box_d:
        deg_y = tar_y * dpx
    else:
        deg_y = 0
    
    # If the target is in the box, indicate this with the box colour
    if deg_y is 0 and deg_x is 0 and found:
        box_clr = SimpleCV.Color.GREEN
    else:
        box_clr = SimpleCV.Color.RED
    
    #output the data
    # not needed if there's no new data to report
    if not lossReported:
        message =   {
                        't'       : millis(),
                        'findTime': findTime,
                        'found'   : found,
                        'tar_px'  : {'x':tar_x, 'y':tar_y},
                        'tar_dg'  : {'x':deg_x, 'y':deg_y}
                    }
        # wait 20 ms to make sure Scan picks up on the last hit
        if not found and millis() - findTime < 100:
            continue
        #socket.send_json(message)
        
        #print "Sent targetData: ",
        #print message
                        
        if lastFound == findTime:
            lossReported = False
            #spam to keep data flowing

