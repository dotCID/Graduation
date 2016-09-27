#!/usr/bin/env python3
"""
Based on the standard pyOSC example "knct_rcv.py" from https://github.com/ptone/pyosc/tree/master/examples
"""

# make it possible to import from parent directory:
import sys
sys.path.insert(0,'..')

from OSC import OSCServer
import time
from globalVars import CHANNEL_BPM

import zmq

# Change terminal window header for easier identification of contents
sys.stdout.write("\x1b]2;Sensors/pyOSCServer.py\x07")

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind(CHANNEL_BPM)

server = OSCServer( ('145.94.192.23', 9001) )
server.timeout = 0
run = True

beatNo = 0


#Arduino-style millis() function for timekeeping
millis = lambda: int(round(time.time() * 1000))

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is 
# set to False
def handle_timeout(self):
    self.timed_out = True

def default_callback(path, tags, args, source):
    return
    
def beat_callback(path, tags, args, source):
    return
    
def bpm_callback(path, tags, args, source):
    BPM = {
            't'  : millis(),
            'bpm': args[0]
          }

    socket.send_json(BPM)
    
    print "BPM:",args[0]

# funny python's way to add a method to an instance of a class
import types
server.handle_timeout = types.MethodType(handle_timeout, server)

server.addMsgHandler( "/live/tempo", bpm_callback )
server.addMsgHandler( "/live/beat", beat_callback )
server.addMsgHandler( "/live/", default_callback )

# user script that's called by the game engine every frame
def each_frame():
    # clear timed_out flag
    server.timed_out = False
    # handle all pending requests then return
    while not server.timed_out:
        server.handle_request()

# simulate a "game engine"
while run:
    # call user script
    each_frame()
server.close()
