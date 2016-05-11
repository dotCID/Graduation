import subprocess  
from SimpleCV import Image
from SimpleCV import Color
import time  


# Test how much fps we get from this
for i in range(1500):
	subprocess.call("raspistill -n -t 1 -w 640 -h 480 -o image.bmp", shell=True)

	img = Image("image.bmp")
	objective = img.colorDistance(color=(255,0,0)).invert()
	blobs = objective.findBlobs()
	
	if blobs:
		img.drawCircle((blobs[-1].x, blobs[-1].y), 10, Color.YELLOW, 3)
	img.show()
