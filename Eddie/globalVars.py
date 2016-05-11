#!/usr/bin/python
'''
Some global variables that should be kept centralised
'''

## ZMQ channels used
CHANNEL_TARGETDATA  = "tcp://127.0.0.1:4001" 
CHANNEL_BEATDATA    = "tcp://127.0.0.1:4002"

## Arduinos
BOT_ARDUINO_ADDRESS = '/dev/ttyACM3'
BOT_ARDUINO_BAUDRATE= 115200

IMU_ARDUINO_ADDRESS = '/dev/ttyUSB0'
IMU_ARDUINO_BAUDRATE= 115200

## Camera
CAMERA_ID_NUMBER = 1
