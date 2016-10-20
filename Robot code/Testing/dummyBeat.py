#!/usr/bin/python
'''
Dummy channel for the Ableton Beat response - used for motion testing without Ableton connection
'''

import sys
sys.path.insert(0, '..')

import zmq, time

from globalVars import CHANNEL_BEAT

## CHANNEL_BEAT
context = zmq.Context()
bt_socket = context.socket(zmq.PUB)
bt_socket.bind(CHANNEL_BEAT)

interval = 1 # second
beatNumber = 0

#get current time in milliseconds
millis = lambda: int(round(time.time() * 1000))

while True:
        bt_msg = { 't'  : millis(),
                   'num': beatNumber
                 }
        
        print bt_msg
        
        bt_socket.send_json(bt_msg)
        
        beatNumber += 1
        time.sleep(interval)
