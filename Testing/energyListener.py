import zmq
import sys
sys.path.insert(0,'..')

from globalVars import CHANNEL_ENERGYDATA

## ZMQ Energy Data channel - Provides data on music energy
eg_context = zmq.Context()
energyChannel = eg_context.socket(zmq.SUB)
energyChannel.setsockopt(zmq.CONFLATE, 1 )
energyChannel.setsockopt(zmq.SUBSCRIBE, '')
energyChannel.connect(CHANNEL_ENERGYDATA)

energyPoller = zmq.Poller()
energyPoller.register(energyChannel, zmq.POLLIN)

while True:
     if len(energyPoller.poll(0)) is not 0:
            energyData = energyChannel.recv_json()
            print energyData
