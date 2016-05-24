#!/user/bin/python
"""
Short script to test the functionality of code.
"""
from Actions import Action_Scan
from Actions import Action_Contact
from Actions import Action
import time
contact = Action_Contact.SpecificAction()
scan = Action_Scan.SpecificAction()
a = Action.Action()

while True:
    contact.execute()

