# Graduation
Code written in the context of my graduation project on Human-Robot Interaction.

## Installation and requirements
### Required Python libraries
This project is written using python 2.7.x.
If you have pip installed, simply use

```
sudo pip install zmq
sudo pip install pyserial
sudo pip install SimpleCV
sudo pip install pygame
sudo pip install https://pypi.python.org/packages/7c/e4/6abb118cf110813a7922119ed0d53e5fe51c570296785ec2a39f37606d85/pyOSC-0.3.5b-5294.tar.gz#md5=ea027aae543aad2ecf7ae51c2a6b6626
```
pip sometimes has an issue finding pyOSC, hence the long url.

### OpenCV
To install OpenCV I recommend using ```git clone https://github.com/jayrambhia/Install-OpenCV``` and following the instructions there.

*My SimpleCV install is currently not working, will update when I figured it out*

### Required Arduino libraries
For the IMU:            ```https://github.com/adafruit/Adafruit_BNO055``` and ```https://github.com/adafruit/Adafruit_Sensor```

For the Servo Shield:   ```https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library```

For the NeoPixels:      ```https://github.com/adafruit/Adafruit_NeoPixel```

## Music software
This project is programmed to work with Ableton Live 9, and requires Ableton Live 9.5 and liveOSC to be able to adjust the music tempo. 
Please note that in order for the communication with liveOSC to work, the IP address in ```globalVars.py``` in this project needs to be set to the IP of the PC running Ableton, and the remoteHost in ```Ableton Live 9/Contents/App-Resources/MIDI Remote Scripts/LiveOSC/RemixNet.py``` needs to correspond to the IP of the PC controlling the robot.
