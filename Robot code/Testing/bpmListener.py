import zmq
import sys
sys.path.insert(0,'..')

from globalVars import CHANNEL_BPM

## ZMQ BPM channel - Provised info on measured music BPM
bpm_context = zmq.Context()
bpmChannel = bpm_context.socket(zmq.SUB)
bpmChannel.setsockopt(zmq.CONFLATE, 1 )
bpmChannel.setsockopt(zmq.SUBSCRIBE, '')
bpmChannel.connect(CHANNEL_BPM)

bpmPoller = zmq.Poller()
bpmPoller.register(bpmChannel, zmq.POLLIN)

while True:
     if len(bpmPoller.poll(0)) is not 0:
            bpmData = bpmChannel.recv_json()
            print bpmData
