#!/usr/bin/python
import time

running = True
s0_finished = False
s1_finished = False
s2_finished = False
s3_finished = False

angle_increment = 0.2
sleep_time = 0.01

s0_min = 5
s1_min = 45
s2_min = 5
s3_min = 35

s0_pos = 5
s1_pos = 45
s2_pos = 5
s3_pos = 90

s0_max = 90
s1_max = 90
s2_max = 90
s3_max = 90
s3_max = 85

while running:
	sh = open("/dev/servoblaster","w")
	sh.write("0="+ str(s0_pos) + "%\n")
	sh.write("1="+ str(s1_pos) + "%\n")
	sh.write("2="+ str(s2_pos) + "%\n")
	sh.write("3="+ str(s3_pos) + "%\n")
	sh.close()

	print("servo 0 pos:" +str(s0_pos))

	if s0_pos <= s0_max and s0_pos >= s0_min: 
		s0_pos+=angle_increment
	else: 
		s0_finished= True
	
	if s1_pos <=s1_max and s1_pos >= s1_min: 
		s1_pos+=angle_increment
	else: 
		s1_finished = True

	if s2_pos <= s2_max and s2_pos >= s2_min: 
		s2_pos+=angle_increment
	else: 
		s2_finished = True

	if s3_pos >= s3_min and s3_pos <= s3_max : 
		s3_pos-=angle_increment
	else: 
		s3_finished = True


	if s0_finished and s1_finished and s2_finished and s3_finished : 
		#running = False
		angle_increment = -1 * angle_increment

		# too lazy to retype, this is vim..
		s0_pos+=angle_increment
		s1_pos+=angle_increment
		s2_pos+=angle_increment
		s3_pos+=angle_increment

		s0_finished = False
		s1_finished = False
		s2_finished = False
		s3_finished = False
		print ("reverse!")

	if s0_pos==5:
		time.sleep(5)
	else:
		time.sleep(sleep_time)

print("End of loop.")

print(s0_pos)
print(s1_pos)
print(s2_pos)
print(s3_pos)

sh = open("/dev/servoblaster", "w")
sh.write("0=50%\n1=85%\n2=80%\n3=85%")
sh.close()
