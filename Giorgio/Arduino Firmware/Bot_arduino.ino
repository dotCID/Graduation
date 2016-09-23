/**
    This sketch reads the serial connection, then actuates the servos as requested within the given limits.
**/

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <Adafruit_NeoPixel.h>

// NeoPixel settings
#define NPX_PIN 6
#define NUMPIXELS 15
#define PXGROUP 5

// NeoPixel patterns
#define PXPAT_PULSE  0
#define PXPAT_BPMUP  1
#define PXPAT_BPMDW -1

// Servo shield connection IDs for servos
#define BH_ID  0
#define BV1_ID 1
#define BV2_ID 2
#define TV_ID  3

// Pulse lengths for "towar dpro MG996R"
#define SERVOMIN  125 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  525 // this is the 'maximum' pulse length count (out of 4096)

// Min, max and default values for the servos
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

Adafruit_NeoPixel pixelstrip = Adafruit_NeoPixel(NUMPIXELS, NPX_PIN, NEO_GRB + NEO_KHZ800);

double BH_pos,BV_pos, TV_pos;
bool fullPrint = false;
bool fullStop = false;

uint32_t red    = pixelstrip.Color(255,   0,   0);
uint32_t green  = pixelstrip.Color(  0, 255,   0);
uint32_t blue   = pixelstrip.Color(  0,   0, 255);
uint32_t white  = pixelstrip.Color(255, 255, 255);
uint32_t purple = pixelstrip.Color(138,  43, 226);
uint32_t none   = pixelstrip.Color(  0,   0,   0);

uint32_t colours[] = { red,  white, red, green, blue};

int npx_currentPattern = PXPAT_PULSE;
unsigned long npx_timer = millis();
uint16_t npx_pulseDelay = 100;

String inputString ="";
bool stringComplete = false;

void setup(){
    // Turn off all pixels at start
    pixelstrip.begin();
    for(int i=0;i<NUMPIXELS;i++){
            pixelstrip.setPixelColor(i, none);
    }
    pixelstrip.show();
    
    Serial.begin(115200);
    
    s_drv.begin();  
    s_drv.setPWMFreq(60);  // Analog servos run at ~60 Hz updates
    
    BH_pos = BH_DEF;
    BV_pos = BV_DEF;
    TV_pos = TV_DEF;
    
    Serial.println(F("Setup done."));
    // Glow when done
    for(int i=0;i<NUMPIXELS;i++){
            pixelstrip.setPixelColor(i, pixelstrip.Color(100, 100, 75));
    }
    pixelstrip.show();
}

void loop(){
    readSerial();
    runMotors();
    ledPattern(npx_currentPattern);
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

/*
    Selects from a choice of patterns and displays them
*/
bool npx_lit = false;
int npx_i = 0;
void ledPattern(int pattern){
    if(pattern == PXPAT_PULSE){
        if(millis() - npx_timer > npx_pulseDelay){
            if(npx_lit){
                // turn all off
                for(int i=0;i<NUMPIXELS;i++){
                    pixelstrip.setPixelColor(i, none);
                }
            }else{
                for(int i=0;i<NUMPIXELS;i++){
                    pixelstrip.setPixelColor(i, purple);
                }
            }
            
            pixelstrip.show();
            npx_lit = !npx_lit;
            npx_timer = millis();
        }
    }else if(pattern == PXPAT_BPMUP){
        if(npx_i<PXGROUP){
            if(millis() - npx_timer > npx_pulseDelay){
                // turn all off
                for(int j=0;j<NUMPIXELS;j++){
                    pixelstrip.setPixelColor(j, none);
                }
              
                // turn on every 5th one
                for(int j=0;j<NUMPIXELS/PXGROUP;j++){
                  if(j!=1){
                    pixelstrip.setPixelColor(PXGROUP*2-npx_i-1, red);
                  }else{
                    pixelstrip.setPixelColor(npx_i+PXGROUP*j, red);
                  }
                }
                
                pixelstrip.show();
                npx_i++;
                npx_timer = millis();
            }
        }else{
            npx_i = 0;
        }
    }else if(pattern == PXPAT_BPMDW){
        if(npx_i<PXGROUP){
            if(millis() - npx_timer > npx_pulseDelay){
                // turn all off
                for(int j=0;j<NUMPIXELS;j++){
                    pixelstrip.setPixelColor(j, none);
                }
              
                // turn on every 5th one
                for(int j=0;j<NUMPIXELS/PXGROUP;j++){
                  if(j!=1){
                    pixelstrip.setPixelColor(npx_i+PXGROUP*j, red);
                  }else{
                    pixelstrip.setPixelColor(PXGROUP*2-npx_i-1, red);
                  }
                }
                
                pixelstrip.show();
                npx_i++;
                npx_timer = millis();
            }
        }else{
            npx_i = 0;
        }
    }
}

