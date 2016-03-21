#!/user/bin/python
import serial, time

H_inc = 0.5
V_inc = -0.4
t_inc = 0.001

running = True
bH_fin = False
bV_fin = False

BH_MIN = 12
BH_MAX = 176
BH_DEF = 94

BV_MIN = 130
BV_MAX = 180
BV_DEF = 155

TH_MIN = 16
TH_MAX = 180
TH_DEF = 98

TV_MIN = 120
TV_MAX = 170
TV_DEF = 145

BH_pos = BH_DEF;
BV_pos = BV_DEF;
TH_pos = TH_DEF;
TV_pos = TV_DEF;


print "connecting"
arduino = serial.Serial('/dev/ttyACM6', 115200, timeout=.1)
time.sleep(1)
print arduino.readline()

def conv(number, oldMin, oldMax, newMin, newMax):
	oldRange = oldMax - oldMin
	newRange = newMax - newMin
	converted = (((number - oldMin)*newRange)/oldRange)+newMin
	return converted

def move():
    arduino.write("BV "+ str(BV_pos) +"\n")
    print arduino.readline()
    
    arduino.write("BH "+ str(BH_pos) +"\n")
    print arduino.readline()

    arduino.write("TV "+ str(TV_pos) +"\n")
    print arduino.readline()

    arduino.write("TH "+ str(TH_pos) +"\n")
    print arduino.readline()

move()
print "ready"
print "..5"
time.sleep(1)
print "..4"
time.sleep(1)
print "..3"
time.sleep(1)
print "..2"
time.sleep(1)
print "..1"
time.sleep(1)

while running:
	if bV_fin and bH_fin:
		V_inc *= -1
		BV_pos += V_inc
		bV_fin = False


	if bH_fin:
		H_inc *= -1
		BH_pos += H_inc
		bH_fin = False
		print("Reversing.")


	if BV_pos >= BV_MIN and BV_pos <= BV_MAX:
		BV_pos += V_inc
	else:
		bV_fin = True

	TV_pos = conv(BV_pos, BV_MIN, BV_MAX, TV_MAX, TV_MIN)


	if BH_pos >= BH_MIN and BH_pos <= BH_MAX:
		BH_pos += H_inc
	else:
		bH_fin = True

	TH_pos = conv(BH_pos, BH_MIN, BH_MAX, TH_MAX, TH_MIN)

	print(str(TV_pos) + "  " + str(BV_pos))
	move()

	time.sleep(t_inc)
