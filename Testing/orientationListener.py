import zmq
import sys
sys.path.insert(0,'..')

from globalVars import CHANNEL_IMU_RAWPOS

## ZMQ IMU_RAWPOS channel - provides data on raw IMU orientation
rawpos_context = zmq.Context()
rawposChannel = rawpos_context.socket(zmq.SUB)
rawposChannel.setsockopt(zmq.CONFLATE, 1 )
rawposChannel.setsockopt(zmq.SUBSCRIBE, '')
rawposChannel.connect(CHANNEL_IMU_RAWPOS)

rawposPoller = zmq.Poller()
rawposPoller.register(rawposChannel, zmq.POLLIN)

while True:
     if len(rawposPoller.poll(0)) is not 0:
            rawposData = rawposChannel.recv_json()
            print rawposData
