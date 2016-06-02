#!/user/bin/python
'''
Logs the data coming in over the positionData channel
'''
import time, zmq

# make it possible to import from parent directory:
import sys
sys.path.insert(0,'..')

from globalVars import CHANNEL_IMU_RAWPOS

## ZMQ Raw orientation channel - Provides data on user orientation
mv_context = zmq.Context()
orientationChannel = mv_context.socket(zmq.SUB)
orientationChannel.setsockopt(zmq.CONFLATE, 1 ) # this tells the subscriber to only get the last message sent since the publisher is probably faster
orientationChannel.setsockopt(zmq.SUBSCRIBE, '')
orientationChannel.connect(CHANNEL_IMU_RAWPOS)

orientationPoller = zmq.Poller()
orientationPoller.register(orientationChannel, zmq.POLLIN)

## Start writing with date and time


with open("orientationDataLog.txt", "a") as fh:
    fh.write("\r\n" + str(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())) + "\r\n\r\n")

while True:
    if len(orientationPoller.poll(0)) is not 0:
        orientationData = orientationChannel.recv_json()
            
        with open("orientationDataLog.txt", "a") as fh:
            fh.write(str(orientationData) + "\r\n")
        
        print "Wrote ", orientationData


