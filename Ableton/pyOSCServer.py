#!/usr/bin/env python3
from OSC import OSCServer
from time import sleep

server = OSCServer( ('145.94.194.158', 9001) )
server.timeout = 0
run = True

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is 
# set to False
def handle_timeout(self):
    self.timed_out = True

def default_callback(path, tags, args, source):
    return
    
def bpm_callback(path, tags, args, source):
    print "BPM:",args[0]

# funny python's way to add a method to an instance of a class
import types
server.handle_timeout = types.MethodType(handle_timeout, server)

server.addMsgHandler( "/live/tempo", bpm_callback )
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
