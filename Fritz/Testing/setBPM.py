#!/user/bin/python
'''
A script to manually (re)set the BPM in Ableton to sensible levels
'''

import sys
sys.path.insert(0,'..')
sys.stdout.write("\x1b]2;Test/setBPM.py\x07")

from OSC import OSCClient
from OSC import OSCMessage
from globalVars import OSC_ABLETON_IP

client = OSCClient()
client.connect((OSC_ABLETON_IP, 9000))

while True:
    raw = raw_input("Enter new BPM: \n")
    try:
        bpm = int(raw)
            
        msg = OSCMessage()
        msg.setAddress("/live/tempo")
        msg.append(bpm)
        client.send(msg)
        
        print "Set BPM to",bpm
    except:
        print "Could not process the input \"", raw, "\""
