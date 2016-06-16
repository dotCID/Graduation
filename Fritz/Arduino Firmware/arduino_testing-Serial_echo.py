#!/user/bin/python
import serial, time

running = True
t_inc = 0.01

arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=.1)
time.sleep(1)
line = arduino.readline().strip()
print line

while running:
    newline = arduino.readline().strip()
    if newline != line: 
        line = newline
        print line
    time.sleep(t_inc)
