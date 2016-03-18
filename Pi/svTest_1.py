#!/usr/bin/python
import time

inc = 5
t_inc = 0.01

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
tH_fin = False

def conv(number, oldMin, oldMax, newMin, newMax):
	oldRange = oldMax - oldMin
	newRange = newMax - newMin
	converted = (((number - oldMin)*newRange)/oldRange)+newMin
	return converted

def move():
	sh = open("/dev/servoblaster","w")
	sh.write(str(bH_pin)+"="+str(botHor)+"us \n")
	sh.write(str(tH_pin)+"="+str(topHor)+"us \n")
	sh.write(str(bH_pin)+"="+str(botHor)+"us \n")
	sh.write(str(tH_pin)+"="+str(topHor)+"us \n")
	sh.close()

move()
time.sleep(1)

while running:
	if bH_fin:
		inc *= -1
		botHor += inc
		topHor -= inc
		bH_fin = False
		print("Reversing.")

	if botHor >= botHor_min and botHor <= botHor_cen:
		botHor += inc
	else:
		bH_fin = True

	topHor = conv(botHor, botHor_min, botHor_cen, topHor_max, topHor_cen)

	print(str(topHor) + "  " + str(botHor))
	move()

	time.sleep(t_inc)
