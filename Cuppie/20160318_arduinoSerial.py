#!/user/bin/python
import serial, time

print "connecting"
arduino = serial.Serial('/dev/ttyACM3', 115200, timeout=.1)

time.sleep(2)

BH_MIN = 0
BH_MAX = 180
BH_DEF = 94

BV_MIN = 90
BV_MAX = 180
BV_DEF = 155

TH_MIN = 0
TH_MAX = 180
TH_DEF = 98

TV_MIN = 40
TV_MAX = 180
TV_DEF = 145

BH_pos = BH_DEF;
BV_pos = BV_DEF;
TH_pos = TH_DEF;
TV_pos = TV_DEF;

arduino.write("BV = "+
