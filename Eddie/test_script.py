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

import time

a = Action.Action()
contact     = Action_Contact.SpecificAction()
scan        = Action_Scan.SpecificAction()
focus       = Action_Focus.SpecificAction()
stevie      = Action_Stevie.SpecificAction()
bored       = Action_Bored.SpecificAction()

while True:
    bored.execute()

