#!/user/bin/python
"""
Short script to test the functionality of code.
"""
from Actions import Action_Scan
from Actions import Action_Contact
from Actions import Action

contact = Action_Contact.SpecificAction()
scan = Action_Scan.SpecificAction()
a = Action.Action()

scan.execute()
contact.execute()
scan.execute()
