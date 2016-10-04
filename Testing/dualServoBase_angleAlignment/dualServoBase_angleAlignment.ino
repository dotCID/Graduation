/*************************************************** 
  This is an example for our Adafruit 16-channel PWM & Servo driver
  Servo test - this will drive 16 servos, one after the other

  Pick one up today in the adafruit shop!
  ------> http://www.adafruit.com/products/815

  These displays use I2C to communicate, 2 pins are required to  
  interface. For Arduino UNOs, thats SCL -> Analog 5, SDA -> Analog 4

  Adafruit invests time and resources providing this open source code, 
  please support Adafruit and open-source hardware by purchasing 
  products from Adafruit!

  Written by Limor Fried/Ladyada for Adafruit Industries.  
  BSD license, all text above must be included in any redistribution
 ****************************************************/

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// called this way, it uses the default address 0x40
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
// you can also call it with a different address you want
//Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x41);

// Depending on your servo make, the pulse width min and max may vary, you 
// want these to be as small/large as possible without hitting the hard stop
// for max range. You'll have to tweak them as necessary to match the servos you
// have!
#define SERVOMIN  175 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  580// this is the 'maximum' pulse length count (out of 4096)

// our servo # counter
uint8_t servonum = 1;

void setup() {
  Serial.begin(115200);
  Serial.println("16 channel Servo test!");

  pwm.begin();
  
  pwm.setPWMFreq(60);  // Analog servos run at ~60 Hz updates

  yield();
}

void setAngle(int angle){
  int pulseWidth_1, pulseWidth_2;
  /*
  if(angle <=90){
    pulseWidth_1 = map(angle, 0, 90, 190, 377); 
    pulseWidth_2 = map(angle, 0, 90, 580, 377);
  }else{
    pulseWidth_1 = map(angle, 91, 180, 377, 580); 
    pulseWidth_2 = map(angle, 91, 180, 377, 175);
  }

  */
  
  pulseWidth_1 = map(angle, 0, 180, 212, 580); 
  pulseWidth_2 = map(angle, 0, 180, 580, 195)-map(abs(angle-90), 0, 90, 18, 0); // This compensation for the nonlinear behaviour of #2 (left) seems to be working the best - though not perfectly
  Serial.print("Set 1: ");
  Serial.print(pulseWidth_1);

  pwm.setPWM(4, 0, pulseWidth_1);
  
  delay(5);
  
  Serial.print("\tSet 2: ");
  Serial.println(pulseWidth_2);
  pwm.setPWM(5, 0, pulseWidth_2);
  
}

void setAngle2(double angle){
  /*
   * More complicated mapping is needed to get the servos aligned well
   */
   
  int pulseWidth_1, pulseWidth_2;

   if(angle >=0 && angle < 10){
    pulseWidth_1 = map(angle, 0, 10, 210, 230); 
    pulseWidth_2 = map(angle, 0, 10, 579, 558);
   }else if(angle < 20){
    pulseWidth_1 = map(angle, 10, 20, 230, 251); 
    pulseWidth_2 = map(angle, 10, 20, 558, 535);    
   }else if(angle < 30){
    pulseWidth_1 = map(angle, 20, 30, 251, 271); 
    pulseWidth_2 = map(angle, 20, 30, 535, 511);
   }else if(angle < 40){
    pulseWidth_1 = map(angle, 30, 40, 271, 292); 
    pulseWidth_2 = map(angle, 30, 40, 511, 488);    
   }else if(angle < 50){
    pulseWidth_1 = map(angle, 40, 50, 292, 312); 
    pulseWidth_2 = map(angle, 40, 50, 488, 465);    
   }else if(angle < 60){
    pulseWidth_1 = map(angle, 50, 60, 312, 333); 
    pulseWidth_2 = map(angle, 50, 60, 465, 441);
   }else if(angle < 70){
    pulseWidth_1 = map(angle, 60, 70, 333, 353); 
    pulseWidth_2 = map(angle, 60, 70, 441, 420);
   }else if(angle < 80){
    pulseWidth_1 = map(angle, 70, 80, 353, 374); 
    pulseWidth_2 = map(angle, 70, 80, 420, 397);
   }else if(angle < 90){
    pulseWidth_1 = map(angle, 80, 90, 374, 395); 
    pulseWidth_2 = map(angle, 80, 90, 397, 376);
   }else if(angle < 100){
    pulseWidth_1 = map(angle, 90, 100, 395, 415)-4; 
    pulseWidth_2 = map(angle, 90, 100, 376, 355);
   }else if(angle < 110){
    pulseWidth_1 = map(angle, 100, 110, 415, 436); 
    pulseWidth_2 = map(angle, 100, 110, 355, 336);
   }else if(angle < 120){
    pulseWidth_1 = map(angle, 110, 120, 436, 456); 
    pulseWidth_2 = map(angle, 110, 120, 336, 316);
   }else if(angle < 130){
    pulseWidth_1 = map(angle, 120, 130, 456, 477); 
    pulseWidth_2 = map(angle, 120, 130, 316, 295);
   }else if(angle < 140){
    pulseWidth_1 = map(angle, 130, 140, 477, 497); 
    pulseWidth_2 = map(angle, 130, 140, 295, 276);
   }else if(angle < 150){
    pulseWidth_1 = map(angle, 140, 150, 497, 518); 
    pulseWidth_2 = map(angle, 140, 150, 276, 257);
   }else if(angle < 160){
    pulseWidth_1 = map(angle, 150, 160, 518, 538); 
    pulseWidth_2 = map(angle, 150, 160, 257, 238);
   }else if(angle < 170){
    pulseWidth_1 = map(angle, 160, 170, 538, 559); 
    pulseWidth_2 = map(angle, 160, 170, 238, 219);
   }else if(angle <= 180){
    pulseWidth_1 = map(angle, 170, 180, 559, 580); 
    pulseWidth_2 = map(angle, 170, 180, 219, 199);
   }


  Serial.print("Set 1: ");
  Serial.print(pulseWidth_1);

  pwm.setPWM(1, 0, pulseWidth_1);
  
  delay(5);
  
  Serial.print("\tSet 2: ");
  Serial.println(pulseWidth_2);
  pwm.setPWM(2, 0, pulseWidth_2);
}

/*        S1  S2
 *   0 = 190 580
 *  90 = 377 377
 * 180 = 580 175 
 */

void loop() {
  // Drive each servo one at a time
// setAngle(90);/*

 for(int i=0; i<=180; i++){
  setAngle(i);
  delay(5);
  if(i%50 == 0) delay(1000);
 }
 delay(2000);
 Serial.println("Pause");
 for(int j=180;j>=0;j--){
  setAngle(j);
  delay(5);
  if(j%50 == 0) delay(1000);
 }
 delay(2000);
 Serial.println("Pause");
}

void temp(){
   for (uint16_t pulselen = SERVOMIN; pulselen < SERVOMAX; pulselen++) {
    pwm.setPWM(1, 0, pulselen);
    pwm.setPWM(2, 0, SERVOMAX - (pulselen - SERVOMIN));
    Serial.print("Set 1: ");
    Serial.print(pulselen);
    Serial.print("\t Set 2: ");
    Serial.print(SERVOMAX - (pulselen - SERVOMIN));
    Serial.println(" (Upward)");
  }

  delay(500);
  
  for (uint16_t pulselen = SERVOMAX; pulselen > SERVOMIN; pulselen--) {
    pwm.setPWM(1, 0, pulselen);
    
    pwm.setPWM(2, 0, SERVOMIN + (SERVOMAX - pulselen));
    Serial.print("Set 1: ");
    Serial.print(pulselen);
    Serial.print("\t Set 2: ");
    Serial.print(SERVOMIN + (SERVOMAX - pulselen));
    Serial.println(" (Downward)");
  }

  delay(500);
}

