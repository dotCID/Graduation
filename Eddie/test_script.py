#!/user/bin/python
"""
Short script to test the functionality of code.
"""
from Actions import Action
from Actions import Action_Contact
from Actions import Action_Scan
from Actions import Action_Focus
from Actions import Action_Stevie
from Actions import Action_Bored

import arduinoInterface as aI

import time
"""
a = Action.Action()
contact     = Action_Contact.SpecificAction()
scan        = Action_Scan.SpecificAction()
focus       = Action_Focus.SpecificAction()
stevie      = Action_Stevie.SpecificAction()
bored       = Action_Bored.SpecificAction()

exit_code = 0
lastCode = 2

while True:
    print "loop running"
    if exit_code == 0:
        if lastCode == 2: 
            lastCode = 5
            exit_code = 5
        elif lastCode == 5: 
            lastCode = 2
            exit_code = 2
    elif exit_code == 2:
        exit_code = scan.execute(150)
    elif exit_code == 5:
        exit_code = bored.execute(150)
        
"""

aI.arduinoConnect("/dev/ttyUSB0", 115200)
angles = aI.getAngles()

aI.moveTo(angles)
print "sleeping"
time.sleep(2)
a  = 0.0
a_dir = 1
while True:    
    aI.arduinoWrite(a, 1)
    
    a+= 0.1*a_dir
    if a > 180:
        a_dir = -1
    elif a < 0:
        a_dir = 1
    time.sleep(0.005)

