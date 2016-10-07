# Graduation
This repository holds the most current versions of the code and CAD models used to create the robot I developed for my graduation project on Human-Robot Interaction.
This repository can be found on GitHub: https://github.com/dotCID/graduation

## Installation and requirements
In order to view the CAD models, SolidWorks 2014 or newer is required. The STL files used to print the robot are also included, in ```/CAD Models/STL```.

### Required Python libraries
This project is written using python 2.7.x.
If you have pip installed, simply use

```
sudo pip install zmq
sudo pip install pyserial
sudo pip install pygame
sudo pip install https://pypi.python.org/packages/7c/e4/6abb118cf110813a7922119ed0d53e5fe51c570296785ec2a39f37606d85/pyOSC-0.3.5b-5294.tar.gz#md5=ea027aae543aad2ecf7ae51c2a6b6626
```
pip sometimes has an issue finding pyOSC, hence the long url.

### SimpleCV
*My SimpleCV install is currently not working, will update when I figured it out*
To install SimpleCV use ```sudo pip install SimpleCV```
To install OpenCV I recommend using ```git clone https://github.com/jayrambhia/Install-OpenCV``` and following the instructions there.

### Required Arduino libraries
The Arduino firmware written for this project is aimed at Arduino Uno / Arduino Pro Mini boards.

The libraries required for this code to work are:

For the IMU:            ```https://github.com/adafruit/Adafruit_BNO055``` and ```https://github.com/adafruit/Adafruit_Sensor```

For the Servo Shield:   ```https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library```

For the NeoPixels:      ```https://github.com/adafruit/Adafruit_NeoPixel```

## Music software
This project is programmed to work with Ableton Live 9, and requires Ableton Live 9.5 and liveOSC to be able to adjust the music tempo. 
The required add-in for Ableton Live 9 can be found in the folder "Ableton".
Please note that in order for the communication with liveOSC to work, the IP address in ```globalVars.py``` in this project needs to be set to the IP of the PC running Ableton, and the remoteHost in ```Ableton Live 9/Contents/App-Resources/MIDI Remote Scripts/LiveOSC/RemixNet.py``` needs to correspond to the IP of the PC controlling the robot.
