import subprocess  
from SimpleCV import Image  
import time  

call(“raspistill -n -t 0 -w %s -h %s -o image.bmp” % 640 480, shell=True)
