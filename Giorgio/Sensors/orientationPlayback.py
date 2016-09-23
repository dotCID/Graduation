#!/user/bin/python
"""
Script to play back data gathered from the IMU by the orientation data logger
"""

# Make it possible to import from parent directory
import sys
sys.path.insert(0,'..')

import zmq
from globalVars import CHANNEL_IMU_RAWPOS

from time import sleep

# Set up ZMQ publishing
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind(CHANNEL_IMU_RAWPOS)

with open("./orientationDataLog.txt", "r") as f:
    for item in f:
        item = item.strip()
        if len(item)>1:
            if item[0] == "{":
                socket.send_json(item)
            else:
                print "Playing back data from",item
        sleep(0.05)
