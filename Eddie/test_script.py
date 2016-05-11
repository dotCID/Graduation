"""
Short script to test the functionality of code.
"""
import Action

a = Action.Action()

done = False

while not done:
    x = a.execute(5)
    if x == 0:
        done = True
