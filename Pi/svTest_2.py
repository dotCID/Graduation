#!/usr/bin/python
import time

H_inc = 5
V_inc = -4
t_inc = 0.01

bV_pin = 1
botVer_max = 2500
botVer_cen = 2200
botVer_min = 1950

tV_pin = 4
topVer_max = 2400
topVer_cen = 2050
topVer_min = 1800

botVer = botVer_cen
topVer = topVer_cen

bH_pin = 0
botHor_min = 625
botHor_max = 2500
botHor_cen = 1525

tH_pin = 2
topHor_min = 650
topHor_max = 2500
topHor_cen = 1575

botHor = botHor_cen
topHor = topHor_cen

running = True
bH_fin = False
bV_fin = False

def conv(number, oldMin, oldMax, newMin, newMax):
	oldRange = oldMax - oldMin
	newRange = newMax - newMin
	converted = (((number - oldMin)*newRange)/oldRange)+newMin
	return converted

def move():
	sh = open("/dev/servoblaster","w")
	sh.write(str(bV_pin)+"="+str(botVer)+"us \n")
	sh.write(str(tV_pin)+"="+str(topVer)+"us \n")
	sh.write(str(bH_pin)+"="+str(botHor)+"us \n")
	sh.write(str(tH_pin)+"="+str(topHor)+"us \n")
	sh.close()

move()
print "ready"
time.sleep(5)

while running:
	if bV_fin and bH_fin:
		V_inc *= -1
		botVer += V_inc
		bV_fin = False


	if bH_fin:
		H_inc *= -1
		botHor += H_inc
		bH_fin = False
		print("Reversing.")


	if botVer >= botVer_min and botVer <= botVer_max:
		botVer += V_inc
	else:
		bV_fin = True

	topVer = conv(botVer, botVer_min, botVer_max, topVer_max, topVer_min)


	if botHor >= botHor_min and botHor <= botHor_max:
		botHor += H_inc
	else:
		bH_fin = True

	topHor = conv(botHor, botHor_min, botHor_max, topHor_max, topHor_min)

#	print(str(topVer) + "  " + str(botVer))
	move()

	time.sleep(t_inc)
