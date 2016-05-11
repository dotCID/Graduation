import subprocess  
from SimpleCV import Image  
import time  

subprocess.call("raspistill -n -t 1 -w 640 -h 480 -o image.bmp", shell=True)
print "Captured image"

img = Image("image.bmp")

print "image loaded"

img = img.edges()    
img.show()    
time.sleep(5)

print "Showing edges"

img = img.binarize()  
img.show()  
time.sleep(5)    

print "Binarizing"

blobs = img.findBlobs()  
for blob in blobs:  
    blob.draw()  
img.show()  

print "Blobs" 
time.sleep(5) 
