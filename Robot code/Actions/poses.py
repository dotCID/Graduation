"""
This file is a database of all poses Giorgio uses. Consolidated into one file for easier changing and debugging.
It would be best for the future to convert all poses to offsets of the default, since (re)construction of the robot changes the angles needed.
"""


## Defaults
pos_default    = ( 67.0,  50.0, 120.0)
pos_min        = (  0.0,   5.0,  20.0)
pos_max        = (180.0, 180.0, 180.0)

## For playing dead
pos_dead       = ( 67.0,  50.0, 120.0)

## Action 1: Contact
contact_joint_positions = [ 180.0 , 70.0, 135.0 ]

## Action 2: Scan
scan_pos_L = [  0.0,  65.0, 140.0]
scan_pos_R = [180.0,  50.0, 125.0]

## Action 3: Acknowledge - switch between two poses of looking at user and one of looking at laptop
ack_pos_C = [ contact_joint_positions[0],  contact_joint_positions[1], contact_joint_positions[2]]
ack_pos_L = [  10.0,   15.0, 100.0]
ack_pos_R = [ contact_joint_positions[0]+10.0,  contact_joint_positions[1]-10.0, contact_joint_positions[2]+10.0]

## Action 4: Stevie
drifting_pos_C = [ 110.0,  90.0, 120.0]
drifting_pos_L = [ 125.0, 100.0, 180.0]
drifting_pos_R = [  95.0,  80.0, 160.0]

## Action 5: Bored
bored_pos_C = [  85.0, 120.0, 180.0]
bored_pos_L = [  25.0, 100.0, 180.0]
bored_pos_R = [ 165.0,  90.0, 160.0]
