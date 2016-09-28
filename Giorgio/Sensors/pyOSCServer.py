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
bpm_socket = context.socket(zmq.PUB)
bpm_socket.bind(CHANNEL_BPM)

# Get the current WiFi IP:
OWN_IP = None
try:
    ## Code originally written by http://stackoverflow.com/users/131264/alexander in http://stackoverflow.com/a/1267524
    import socket
    OWN_IP = ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
except:
    print "Could not find the local WiFi IP."
    while True:
        continue


try:
    server = OSCServer( (OWN_IP, 9001) )
    server.timeout = 0
    run = True
    print "Created the server at ",OWN_IP,". Listening.."
except:
    print "Could not create server."
    while True:
        continue

#Arduino-style millis() function for timekeeping
millis = lambda: int(round(time.time() * 1000))

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is 
# set to False
def handle_timeout(self):
    self.timed_out = True

def default_callback(path, tags, args, source):
    return
    
def bpm_callback(path, tags, args, source):
    print "BPM:",args[0]
    BPM = {
            't'  : millis(),
            'bpm': args[0]
          }

    bpm_socket.send_json(BPM)
    
def error_callback(path, tags, args, source):
    print "\nInvalid input sent; Ableton returned:\n",args, "\n"

# funny python's way to add a method to an instance of a class
import types
server.handle_timeout = types.MethodType(handle_timeout, server)

server.addMsgHandler( "/live/tempo", bpm_callback )
server.addMsgHandler( "/live/", default_callback )
server.addMsgHandler( "/live/beat", default_callback)

server.addMsgHandler( "/remix/error", error_callback)

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
