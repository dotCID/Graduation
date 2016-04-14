import SimpleCV, time

display = SimpleCV.Display()
cam = SimpleCV.Camera(1)
normaldisplay = True


while display.isNotDone():

    if display.mouseRight:
	    normaldisplay = not(normaldisplay)
	    print "Display Mode:", "Normal" if normaldisplay else "Segmented" 

    img = cam.getImage().flipHorizontal()
    dist = img.colorDistance((90, 240, 255)).invert()
    segmented = dist.stretch(220,255)
    blobs = segmented.findBlobs()
    if blobs:
	   for blob in blobs:
            img.drawCircle((blob.x, blob.y), 5,SimpleCV.Color.BLUE,3)

    if normaldisplay:
	    img.show()
    else:
        segmented.show()
        
