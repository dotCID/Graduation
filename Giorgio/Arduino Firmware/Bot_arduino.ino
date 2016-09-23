/**
    This sketch reads the serial connection, then actuates the servos as requested within the given limits.
**/

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define BH_ID  0
#define BV1_ID 1
#define BV2_ID 2
#define TV_ID  3

double BH_pos,BV_pos, TV_pos;
bool fullPrint = false;
bool fullStop = false;

// Pulse lengths for "towar dpro MG996R"
#define SERVOMIN  125 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  525 // this is the 'maximum' pulse length count (out of 4096)

#define BH_MIN 0
#define BH_MAX 180
#define BH_DEF 170

#define BV_MIN 0
#define BV_MAX 180
#define BV_DEF 30

#define TV_MIN 0
#define TV_MAX 180
#define TV_DEF 75

// called this way, it uses the default address 0x40
Adafruit_PWMServoDriver s_drv = Adafruit_PWMServoDriver();

String inputString ="";
bool stringComplete = false;

void setup(){
    Serial.begin(115200);
    
    s_drv.begin();
  
    s_drv.setPWMFreq(60);  // Analog servos run at ~60 Hz updates
    
    BH_pos = BH_DEF;
    BV_pos = BV_DEF;
    TV_pos = TV_DEF;
    
    Serial.println(F("Setup done."));
}

void loop(){
    readSerial();
    runMotors();
}

/*
    A function to check whether a complete string  (i.e. one ending in \n) has been sent over the serial connection. It then responds accordingly.
  Possible commands:
  start   -   Starts the motor actuation
  stop    -   Stops motor actuation
  home    -   Return to default angles
  on      -   Turn LED 13 on
  off     -   Turn LED 13 off
  BH #.#
  BV #.#
  TH #.#
  TV #.#
*/
void readSerial(){
  while (Serial.available()) {
    char inChar = (char)Serial.read(); 
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    } 
  }
  
  if(stringComplete) {
      if(inputString == "stop\n"){
          Serial.println(F("Stopping."));
          fullStop = true;
    }else if(inputString == "start\n"){
          Serial.println(F("Starting."));
          fullStop = false;
    }else if(inputString == "home\n"){
        Serial.println(F("Returning to default angles."));
        BH_pos = BH_DEF;
        BV_pos = BV_DEF;
        TV_pos = TV_DEF;
    }else if(inputString == "on\n"){
      Serial.println(F("LED on"));
        digitalWrite(13,HIGH);
    }else if(inputString == "off\n"){
      Serial.println(F("LED off"));
        digitalWrite(13,LOW);
    }if(inputString.startsWith("BH")){
      String val = inputString.substring(3,inputString.length());
      BH_pos = val.toFloat();
      if(BH_pos<BH_MIN) BH_pos = BH_MIN;
      if(BH_pos>BH_MAX) BH_pos = BH_MAX;
      
      if(fullPrint) Serial.print(F("BH_pos is now "));Serial.println(BH_pos);
    }if(inputString.startsWith("BV")){
      String val = inputString.substring(3,inputString.length());
      BV_pos = val.toFloat();
      if(BV_pos<BV_MIN) BV_pos = BV_MIN;
      if(BV_pos>BV_MAX) BV_pos = BV_MAX;
      
      if(fullPrint) Serial.print(F("BV_pos is now "));Serial.println(BV_pos);
    }if(inputString.startsWith("TV")){
      String val = inputString.substring(3,inputString.length());
      TV_pos = val.toFloat();
      if(TV_pos<TV_MIN) TV_pos = TV_MIN;
      if(TV_pos>TV_MAX) TV_pos = TV_MAX;
      
      if(fullPrint) Serial.print(F("TV_pos is now "));Serial.println(TV_pos);
    }
  }
}

/*
    This function moves the servos to the currently set positions if they adhere to the limits.
*/
void runMotors(){
    if(!fullStop){
        if((BH_pos >= BH_MIN) && (BH_pos <= BH_MAX)){
            s_drv.setPWM(BH_ID, 0, degree2Pulse(BH_pos));
        }
        
        if((BV_pos >= BV_MIN) && (BV_pos <= BV_MAX)){
            s_drv.setPWM(BV1_ID, 0, degree2Pulse(BV_pos));
            s_drv.setPWM(BV2_ID, 0, degree2Pulse(180.0 - BV_pos)); // control second motor inversely
        }
        
        if((TV_pos >= TV_MIN) && (TV_pos <= TV_MAX)){
            s_drv.setPWM(TV_ID, 0, degree2Pulse(TV_pos));
        }
    }else{
        //Serial.print(F("All motion is currently stopped. Please send \"start\" to start moving."));
    }
}

/* 
    Converts positions in degrees to pulsewidth signals for the driver 

*/
uint16_t degree2Pulse(int degree){
    return (uint16_t) map(degree, 0.0, 180.0, SERVOMIN, SERVOMAX);
}

