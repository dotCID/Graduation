"""
This file is a database of all poses Fritz uses. Consolidated into one file for easier changing and debugging.
"""


## Defaults
pos_default    = (105.0, 130.0,  75.0)
pos_min        = ( 10.0,  10.0,  20.0)
pos_max        = (170.0, 160.0, 160.0)

## For playing dead
pos_dead       = (170, 30, 75 )

## Action 1: Contact
contact_joint_positions = [ 94.0 , 100.0, 135.0 ]

## Action 2: Scan
scan_pos_L = [ 10.0, 110.0, 135.0]
scan_pos_R = [105.0,  90.0, 145.0]

## Action 3: Acknowledge
ack_pos_C = [ 94.0,  110.0, 130.0]
ack_pos_L = [ 85.0,  90.0, 140.0]
ack_pos_R = [ 105.0,  120.0, 120.0]

## Action 4: Stevie
drifting_pos_C = [ 110.0, 130.0, 120.0]
drifting_pos_L = [ 125.0, 140.0,  40.0]
drifting_pos_R = [  95.0, 120.0,  70.0]

## Action 5: Bored
bored_pos_C = [  85.0, 160.0,  50.0]
bored_pos_L = [  25.0, 160.0,  60.0]
bored_pos_R = [ 165.0, 160.0,  50.0]
