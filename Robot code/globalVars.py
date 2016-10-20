#!/usr/bin/python
'''
Some global variables that should be kept centralised
'''

## ZMQ channels used
CHANNEL_TARGETDATA  = "tcp://127.0.0.1:4001" # Data on computer vision target
CHANNEL_ACCELDATA   = "tcp://127.0.0.1:4002" # Data on IMU average acceleration
CHANNEL_ENERGYDATA  = "tcp://127.0.0.1:4004" # Energy level from ControlBox
CHANNEL_MODE        = "tcp://127.0.0.1:4005" # Movement mode
CHANNEL_BPM         = "tcp://127.0.0.1:4006" # BPM from Ableton or ControlBox
CHANNEL_BEAT        = "tcp://127.0.0.1:4007" # Beats sent out by Ableton (numbered by Ableton)

CHANNEL_IMU_RAWACCEL= "tcp://127.0.0.1:4008"
CHANNEL_IMU_RAWPOS  = "tcp://127.0.0.1:4009"

CHANNEL_PEDAL       = "tcp://127.0.0.1:4010" # Current state of the foot pedal

## OSC Addresses
OSC_ABLETON_IP      = "192.168.178.10"

## Arduinos 
BOT_ARDUINO_ADDRESS = '/dev/ttyUSB0'
BOT_ARDUINO_BAUDRATE= 115200

IMU_ARDUINO_ADDRESS = '/dev/ttyUSB1'
IMU_ARDUINO_BAUDRATE= 115200

PEDAL_ARDUINO_ADDRESS = '/dev/ttyACM3'
PEDAL_ARDUINO_BAUDRATE = 115200

## Camera
CAMERA_ID_NUMBER = 1

## Exit codes for the Actions
EXIT_CODE_DONE  = 0
EXIT_CODE_ERROR = -15

# Continue to a different Action:
EXIT_CODE_CONTACT  = 1
EXIT_CODE_SCAN     = 2
EXIT_CODE_ACK      = 3
EXIT_CODE_STEVIE   = 4
EXIT_CODE_BORED    = 5


## Margins and Thresholds
MARGIN_USER_CONTACT         = 30.0
THRESHOLD_EDIFF             = 0.2     # Energy difference in movement needed for BPM adjustment

ENERGY_CALC_MEASURES        = 1.0     # Measures over which user input on BPM adjustment is counted
BPM_SHIFT_WAIT_MEASURES     = 1.0     # Wait for this amount of measures to change BPM
BPM_SHIFT_CNTDWN_MEASURES   = 1.0     # Count down over this amount of measures

ENERGY_SAMPLE_LENGTH        = 5       # Average acceleration is calculated over this amount of measurements
ENERGY_AVG_LENGTH           = 120     # Amount of samples over which long term energy is taken ( 4 samples =~ 1 second)
BPM_DIFF                    = 5.0     # Maximum BPM shift if user input was detected
MAX_PED_RESP_TIME           = 5.0     # How long the beat mod is a response to user input


## Debug values
printing  = True
TEST_MODE_SLOW = False
