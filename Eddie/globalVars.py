#!/usr/bin/python
'''
Some global variables that should be kept centralised
'''

## ZMQ channels used
CHANNEL_TARGETDATA  = "tcp://127.0.0.1:4001" 
CHANNEL_BEATDATA    = "tcp://127.0.0.1:4002" # Not intended to be used for Eddie, but kept for Fritz
CHANNEL_MOVEMENTDATA= "tcp://127.0.0.1:4003"
CHANNEL_ENERGYDATA  = "tcp://127.0.0.1:4004"
CHANNEL_MODE        = "tcp://127.0.0.1:4005"
CHANNEL_BPM         = "tcp://127.0.0.1:4006"
CHANNEL_JOINTDATA   = "tcp://127.0.0.1:4007"

## Arduinos
BOT_ARDUINO_ADDRESS = '/dev/ttyACM3'
BOT_ARDUINO_BAUDRATE= 115200

IMU_ARDUINO_ADDRESS = '/dev/ttyUSB0'
IMU_ARDUINO_BAUDRATE= 115200

## Camera
CAMERA_ID_NUMBER = 1

## Exit codes for the Actions
EXIT_CODE_DONE  = 0
EXIT_CODE_ERROR = -1

# Continue to a different Action:
EXIT_CODE_A1    = 1
EXIT_CODE_A2    = 2
EXIT_CODE_A3    = 3
EXIT_CODE_A4    = 4
EXIT_CODE_A5    = 5

## Last known user positions
user_contact_angles = {
                        't' : 0,
                        'x' : 0.0,
                        'y' : 0.0,
                        'z' : 0.0
                      }
joint_positions     = [ 90.0 , 90.0, 90.0 ]

