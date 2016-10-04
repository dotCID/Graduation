#!/usr/bin/python
"""
The basic idea of this calculation is to take the sum of the magnitude 
of the acceleration vectors over a set time period, which is then used
as an indicator for how strongly the user moved. 
If the user moves the same amount but quicker, the summed acceleration 
will increase; if the user moves more but at the same frequency, it 
will also increase.

F.I.:
sum(len(a_vectors)) over 1 second
"""

import sys
sys.path.insert(0,'..')

sys.stdout.write("\x1b]2;Sensors/beatDetect.py\x07")

import time, zmq

from globalVars import CHANNEL_ACCELDATA
from globalVars import CHANNEL_IMU_RAWACCEL

from globalVars import ENERGY_AVG_LENGTH
from globalVars import ENERGY_SAMPLE_LENGTH

context = zmq.Context()
acceldata = context.socket(zmq.PUB)
acceldata.bind(CHANNEL_ACCELDATA)

## ZMQ Raw Accel channel - Raw accelleration from the IMU
ra_context = zmq.Context()
rawAccelChannel = ra_context.socket(zmq.SUB)
rawAccelChannel.setsockopt(zmq.CONFLATE, 1 )
rawAccelChannel.setsockopt(zmq.SUBSCRIBE, '')
rawAccelChannel.connect(CHANNEL_IMU_RAWACCEL)

accelPoller = zmq.Poller()
accelPoller.register(rawAccelChannel, zmq.POLLIN)

summing_started     = False                     # Keep track of the summing interval
summing_start_time  = 0

a_short_avg_list    = [0]*ENERGY_SAMPLE_LENGTH  # Sampling window for average acceleration
a_short_avg         = 0                         # Average of the list
a_long_avg_list     = [0]*ENERGY_AVG_LENGTH*ENERGY_SAMPLE_LENGTH     # Long-term average used by energy change calculations
a_long_avg          = 0                         # Average of the list

# Arduino-style millis() function for timekeeping
millis = lambda: int(round(time.time() * 1000))
    
def listShift(ls, newEntry):
    '''
    @author MCW
    Shifts the contents of a list and adds the new entry to the end
    '''
    for i in range(len(ls)-1):
        ls[i] = ls[i+1]
    ls[-1] = newEntry
    
    return ls


print "--------------\nBeat.py is now running.\n--------------\n"

while True:    

    # read from ZMQ; only continue if there is new data to process
    # Data is sent from the IMU at ~50ms intervals (50ms + time required to print out the messages)
    if len(accelPoller.poll(0)) is not 0:
        rawAccelData = rawAccelChannel.recv_json()

        # Calculate the vector length, compensated for gravity
        a_len = (rawAccelData['x']**2 + rawAccelData['y']**2 + rawAccelData['z']**2)**0.5  # sqrt(x^2 + y^2 + z^2)
        a_len -= 9.8                                                                       # The IMU does not compensate for gravity if using raw data
        a_len = abs(a_len)                                                                 # After compensation negative values are possible, direction is not of interest to us (otherwise we'd always end up averaging 0)

        # Append data to the list        
        a_short_avg_list = listShift(a_short_avg_list, a_len)
        a_long_avg_list = listShift(a_long_avg_list, a_len)
        
        # Compute averages
        a_short_avg = sum(a_short_avg_list) / len(a_short_avg_list)
        a_long_avg = sum(a_long_avg_list) / len(a_long_avg_list)
        
        # Send data
        msg = {
                't'           : millis(),
                'a_avg_short' : a_short_avg,
                'a_avg_long'  : a_long_avg
              }
        # MCW: Send message
        print "Sent to CHANNEL_ACCELDATA: ", msg
        acceldata.send_json(msg)
