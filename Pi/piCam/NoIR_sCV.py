import subprocess  
from SimpleCV import Image  
import time  

call(“raspistill -n -t 0 -w %s -h %s -o image.bmp” % 640 480, shell=True)

img = img.edges()    
img.show()    
time.sleep(5)


img = img.binarize()  
img.show()  
time.sleep(5)    


img = img.findBlobs()  
for blob in blobs:  
    blob.draw()  
img.show()  
time.sleep(5) 
