'''
This script uses SimpleCV to find a blue LED and report its position relative to the camera view centre and whether it is inside the target area.
'''
#!/user/bin/python
import time, math, SimpleCV
import zmq

printing = True

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


context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://127.0.0.1:4999")


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
status = "Lost"
findTime = 0
lastFound = findTime
lossReported = False

while display.isNotDone():
    target = search()
    
    if target is not None:
        tar_x = target[0]-width/2 
        tar_y = target[1]-height/2
        findTime = millis()
        status = "Found"
        lossReported = False
    else:
        status = "Lost"
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
        message =   str(findTime) + ": " +\
                    status+ " " + \
                    "("+str(tar_x)+","+str(tar_y)+")" + " " +\
                    "["+str(deg_x)+","+str(deg_y)+"]"

        socket.send(message)
                        
        if lastFound == findTime:
            lossReported = True

