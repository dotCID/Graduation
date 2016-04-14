'''
This script uses SimpleCV to find a blue LED and report its position relative to the camera view centre and whether it is inside the target area.
'''
#!/user/bin/python
import time, math, SimpleCV
import zmq, json
from globalVars import CHANNEL_TARGETDATA
from globalVars import CAMERA_ID_NUMBER

printing = True

dpx = 0.0725 # approximate amount of degrees per pixel

width = 640
height = 480
display = SimpleCV.Display()
cam = SimpleCV.Camera(CAMERA_ID_NUMBER, {"width":width,"height":height})

#target box for the marker
box_d = 20
yTgt = (height/2-box_d, height/2+box_d)
xTgt = (width/2-box_d, width/2+box_d)

centre = (height/2, width/2)


context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind(CHANNEL_TARGETDATA)


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
        
        socket.send_json(message)
        print "Sent message: ",
        print message
                        
        if lastFound == findTime:
            lossReported = True

