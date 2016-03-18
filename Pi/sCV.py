#!/user/bin/python
import time
from SimpleCV import *

display = Display()
cam = Camera(0, {"width":320, "height":240})

while display.isNotDone():
	img = cam.getImage()
	img.flipHorizontal()
	img.show()
	time.sleep(1)
