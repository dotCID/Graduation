#!/user/bin/python
import serial, time, math

#move from one pose to another based on accelleration
dt = 0.001

dv = 0.005
vmax = 25
vmin = 0.01

BH_v = vmin
BH_tRem = 0

BH_start = 0
BH_end = 180

BH_pos = BH_start

BH_accel = True
BH_decel = False

'''
# calculate v based on time(steps) remaining:
def calc_v(v, tRem):
    t_needed = (v*v)/(2*dv)
    print "t_needed: ",
    print t_needed
    
    if t_needed < tRem:
        if v+dv < vmax:
            v+=dv
    else:
        if v-dv > vmin:
            v-=dv
    return v
'''

def calc_v(v, tRem):
    global BH_accel, BH_decel
    
    if BH_accel:
        t_needed = (v*v)/(2*dv)
        
        if t_needed >= tRem:
            BH_accel = False
            BH_decel = True
        else:
            if v+dv < vmax:
                v+=dv
    if BH_decel:
        if v-dv > vmin:
            v-=dv
    
    if v == vmin:
        BH_accel = True
        BH_decel = False
    
    return v


def move():
    arduino.write("BH "+ str(BH_pos) +"\n")
    print arduino.readline()
    

print "connecting"
arduino = serial.Serial('/dev/ttyACM6', 115200, timeout=.1)
time.sleep(1)
print arduino.readline()

while True:
    while BH_pos < BH_end:
        BH_tRem = math.floor(abs(BH_pos - BH_end)/BH_v)
        print "tRem: ",
        print BH_tRem
        BH_v = calc_v(BH_v, BH_tRem)
        print "BH_v: ",
        print BH_v
        BH_pos += BH_v  # moving in positive direction
        move()
        time.sleep(dt)
    
    break
    time.sleep(3)
    
    while BH_pos > BH_start:
        BH_tRem = abs(BH_start - BH_pos)/BH_v
        print "tRem: ",
        print BH_tRem
        BH_v = calc_v(BH_v, BH_tRem)
        print "BH_v: ",
        print BH_v
        BH_pos -= BH_v  # moving in negative direction
        move()
        time.sleep(dt)
    
    time.sleep(3)
