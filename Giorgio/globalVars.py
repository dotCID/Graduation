#!/usr/bin/python
'''
Some global variables that should be kept centralised
'''

## ZMQ channels used
CHANNEL_TARGETDATA  = "tcp://127.0.0.1:4001" # Data on computer vision target
CHANNEL_BEATDATA    = "tcp://127.0.0.1:4002" # Data on IMU beats
CHANNEL_ENERGYDATA  = "tcp://127.0.0.1:4004" # Energy level from ControlBox
CHANNEL_MODE        = "tcp://127.0.0.1:4005" # Movement mode
CHANNEL_BPM         = "tcp://127.0.0.1:4006" # BPM from Ableton or ControlBox

CHANNEL_IMU_RAWACCEL= "tcp://127.0.0.1:4007"
CHANNEL_IMU_RAWPOS  = "tcp://127.0.0.1:4008"

CHANNEL_PEDAL       = "tcp://127.0.0.1:4009" # Current state of the foot pedal

## OSC Addresses
OSC_ABLETON_IP      = "145.94.159.149"

## Arduinos 
BOT_ARDUINO_ADDRESS = '/dev/ttyUSB0'
BOT_ARDUINO_BAUDRATE= 115200

IMU_ARDUINO_ADDRESS = '/dev/ttyUSB1'
IMU_ARDUINO_BAUDRATE= 115200

CONTROLBOX_ARDUINO_ADDRESS = '/dev/ttyACM3'
CONTROLBOX_ARDUINO_BAUDRATE = 115200

PEDAL_ARDUINO_ADDRESS = '/dev/ttyACM5'
PEDAL_ARDUINO_BAUDRATE = 115200

## Camera
CAMERA_ID_NUMBER = 1

## Exit codes for the Actions
EXIT_CODE_DONE  = 0
EXIT_CODE_ERROR = -15

# Continue to a different Action:
EXIT_CODE_CONTACT  = 1
EXIT_CODE_SCAN     = 2
EXIT_CODE_FOCUS    = 3
EXIT_CODE_STEVIE   = 4
EXIT_CODE_BORED    = 5

## Margins
MARGIN_USER_CONTACT = 30.0
THRESHOLD_EDIFF = 20.0      # Energy difference in movement needed for BPM adjustment
ENERGY_CALC_TIME = 5.0      # Seconds over which user input on BPM adjustment is counted
BPM_DIFF = 10.0             # BPM shift if user input was detected

## Debug values
printing  = True
TEST_MODE_SLOW = False
