#!/usr/bin/python
import time

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

running = True
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
	sh.close()

move()
time.sleep(1)

while running:
	if bV_fin:
		V_inc *= -1
		botVer += V_inc
		bV_fin = False
		print("Reversing.")

	if botVer >= botVer_min and botVer <= botVer_max:
		botVer += V_inc
	else:
		bV_fin = True

	topVer = conv(botVer, botVer_min, botVer_max, topVer_max, topVer_min)

	print(str(topVer) + "  " + str(botVer))
	move()

	time.sleep(t_inc)
