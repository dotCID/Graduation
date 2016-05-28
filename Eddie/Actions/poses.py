"""
This file is a database of all poses Eddie uses. Consolidated into one file for easier changing and debugging.
"""


## Defaults
pos_default    = ( 50.0,  75.0,  90.0)
pos_min        = (  0.0,  30.0,   0.0)
pos_max        = (180.0, 120.0, 180.0)

## Action 1: Contact

## Action 2: Scan
#these are ideal, but without stronger motors they cannot be achieved
#scan_pos_L = [  0.0,  40.0,  30.0]
#scan_pos_R = [180.0,  40.0,  30.0]

scan_pos_L = [  0.0, 70.0, 105.0]
scan_pos_R = [180.0, 50.0, 125.0]

## Action 3: Focus
focus_pos_C = [  50.0,  55.0, 135.0]
focus_pos_L = [  30.0,  45.0, 110.0]
focus_pos_R = [  70.0,  40.0, 100.0]

## Action 4: Stevie
drifting_pos_C = [  35.0,  90.0, 120.0]
drifting_pos_L = [  45.0, 105.0,  90.0]
drifting_pos_R = [  55.0,  80.0, 100.0]

## Action 5: Bored
bored_pos_C = [  85.0, 110.0,  50.0]
bored_pos_L = [  25.0, 110.0,  30.0]
bored_pos_R = [ 165.0, 110.0,  60.0]
