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
#define PXPAT_BPMSAME 2

// Servo shield connection IDs for servos
#define BH_ID  0
#define BV1_ID 1
#define BV2_ID 2
#define TV_ID  3

// Pulse lengths for "towar dpro MG996R"
#define TWP_MIN  125 // this is the 'minimum' pulse length count (out of 4096)
#define TWP_MAX  525 // this is the 'maximum' pulse length count (out of 4096)

#define FTK_MIN  175
#define FTK_MAX  580

// Min, max and default values for the servos
#define BH_MIN 0
#define BH_MAX 180
#define BH_DEF 67

#define BV_MIN 0
#define BV_MAX 180
#define BV_DEF 50

#define TV_MIN 0
#define TV_MAX 180
#define TV_DEF 75

// called this way, it uses the default address 0x40
Adafruit_PWMServoDriver s_drv = Adafruit_PWMServoDriver();

Adafruit_NeoPixel pixelstrip = Adafruit_NeoPixel(NUMPIXELS, NPX_PIN, NEO_GRB + NEO_KHZ800);

double BH_pos,BV_pos, TV_pos;
bool fullPrint = false;
bool fullStop = false; // if true, all servos initiate to 90 degrees by default instead of the above defaults

uint32_t red    = pixelstrip.Color(255,   0,   0);
uint32_t green  = pixelstrip.Color(  0, 255,   0);
uint32_t blue   = pixelstrip.Color(  0,   0, 255);
uint32_t white  = pixelstrip.Color(255, 255, 255);
uint32_t purple = pixelstrip.Color(138,   0, 226);
uint32_t none   = pixelstrip.Color(  0,   0,   0);

uint32_t colours[] = { red,  white, red, green, blue};

int npx_currentPattern = PXPAT_PULSE;
unsigned long npx_timer = millis();
uint16_t npx_pulseDelay = 300;

String inputString ="";
bool stringComplete = false;

void setup(){
    // Turn off all pixels at start
    pixelstrip.begin();
    for(int i=0;i<NUMPIXELS;i++){
            pixelstrip.setPixelColor(i, none);
    }
    pixelstrip.show();
    
    // Glow when starting
    for(int i=0;i<NUMPIXELS;i++){
            pixelstrip.setPixelColor(i, pixelstrip.Color(100, 100, 75));
    }
    pixelstrip.show();
    
    Serial.begin(115200);
    
    s_drv.begin();  
    s_drv.setPWMFreq(60);  // Analog servos run at ~60 Hz updates
    
    BH_pos = BH_DEF;
    BV_pos = BV_DEF;
    TV_pos = TV_DEF;
    
    delay(1000);
    
    Serial.println(F("Setup done."));
    
}

void loop(){
    readSerial();
    runMotors();
    ledPattern(npx_currentPattern);
}

/*
    A function to check whether a complete string  (i.e. one ending in \n) has been sent over the serial connection. It then responds accordingly.
  Possible commands:
  start         -   Starts the motor actuation
  stop          -   Stops motor actuation
  BH #.#
  BV #.#
  TH #.#
  TV #.#
  bpmSame       -   Flash to indicate no change
  bpmUp         -   Quick pattern up
  bpmDown       -   Quick pattern down
  bpmCountUp    -   Count up from the bottom LED
  bpmCountDown  -   Count down from the top LED
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
      if(inputString.startsWith("stop")){
          Serial.println(F("Stopping."));
          fullStop = true;
    
    }else if(inputString.startsWith("start")){
          Serial.println(F("Starting."));
          fullStop = false;
    
    }else if(inputString.startsWith("BH")){
      String val = inputString.substring(3,inputString.length());
      BH_pos = val.toFloat();
      if(BH_pos<BH_MIN) BH_pos = BH_MIN;
      if(BH_pos>BH_MAX) BH_pos = BH_MAX;
      
      if(fullPrint) Serial.print(F("BH_pos is now "));Serial.println(BH_pos);
      
     if(fullPrint) Serial.print("Set BH to ");
     if(fullPrint) Serial.print((int)degree2Pulse(BH_pos, "TWP"));
     
    }else if(inputString.startsWith("BV")){
      String val = inputString.substring(3,inputString.length());
      BV_pos = val.toFloat();
      if(BV_pos<BV_MIN) BV_pos = BV_MIN;
      if(BV_pos>BV_MAX) BV_pos = BV_MAX;
      
      if(fullPrint) Serial.print(F("BV_pos is now "));Serial.println(BV_pos);
      
      
      if(fullPrint) {   Serial.print("Set BV to ");
                        Serial.print(map(BV_POS, 0, 180, 212, 580));Serial.print("\t");Serial.println(map(BV_POS, 0, 180, 580, 195)-map(abs(BV_POS-90), 0, 90, 18, 0));
                    }
      
    }else if(inputString.startsWith("TV")){
      String val = inputString.substring(3,inputString.length());
      TV_pos = val.toFloat();
      if(TV_pos<TV_MIN) TV_pos = TV_MIN;
      if(TV_pos>TV_MAX) TV_pos = TV_MAX;
      
      if(fullPrint) Serial.print(F("TV_pos is now "));Serial.println(TV_pos);
    
    }else if(inputString.startsWith("bpmSame")){
        npx_currentPattern = PXPAT_PULSE;
        npx_pulseDelay = 50;
    
    }else if(inputString.startsWith("bpmUp")){
        npx_currentPattern = PXPAT_BPMUP;
        npx_pulseDelay = 100;
    
    }else if(inputString.startsWith("bpmDown")){
        npx_currentPattern = PXPAT_BPMDW;
        npx_pulseDelay = 100;
    
    }else if(inputString.startsWith("bpmCountUp")){
        String val = inputString.substring(10,inputString.length());
        int pxdelay = val.toInt();
        npx_currentPattern = PXPAT_BPMUP;
        npx_pulseDelay = pxdelay;
    
    }else if(inputString.startsWith("bpmCountDown")){
        String val = inputString.substring(12,inputString.length());
        int pxdelay = val.toInt();
        npx_currentPattern = PXPAT_BPMDW;
        npx_pulseDelay = pxdelay;
    
    }
    inputString = "";
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
            // These motors are quite finicky in use, require different min/max pulses and some compensation for the error in servo 2
            pulseWidth_1 = map(BV_POS, 0, 180, 212, 580); 
            pulseWidth_2 = map(BV_POS, 0, 180, 580, 195)-map(abs(BV_POS-90), 0, 90, 18, 0); // This compensation for the nonlinear behaviour of #2 (left) seems to be working the best - though not perfectly
          
            s_drv.setPWM(BV1_ID, 0, pulseWidth_1);
            s_drv.setPWM(BV2_ID, 0, pulseWidth_2);
        }
        
        if((TV_pos >= TV_MIN) && (TV_pos <= TV_MAX)){
            s_drv.setPWM(TV_ID, 0, degree2Pulse(TV_pos));
        }
    }else{
        //Serial.print(F("All motion is currently stopped. Please send \"start\" to start moving."));
    }
}

/* 
    Converts positions in degrees to pulsewidth signals for the driver. Used for the BH and TV motors.
*/
uint16_t degree2Pulse(double degree){
    return (uint16_t) map(degree, 0.0, 180.0, TWP_MIN, TWP_MAX);
}

/*
    Selects from a choice of patterns and displays them
*/
bool npx_lit = false;
int npx_i = 0;
void ledPattern(int pattern){
    if(!fullStop){
        if(pattern == PXPAT_PULSE){
            npx_pulseDelay = 300;
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
                        pixelstrip.setPixelColor(PXGROUP*2-npx_i-1, blue);
                      }else{
                        pixelstrip.setPixelColor(npx_i+PXGROUP*j, blue);
                      }
                    }
                    
                    pixelstrip.show();
                    npx_i++;
                    npx_timer = millis();
                }
            }else{
                npx_i = 0;
                npx_currentPattern = PXPAT_PULSE;
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
                        pixelstrip.setPixelColor(npx_i+PXGROUP*j, green);
                      }else{
                        pixelstrip.setPixelColor(PXGROUP*2-npx_i-1, green);
                      }
                    }
                    
                    pixelstrip.show();
                    npx_i++;
                    npx_timer = millis();
                }
            }else{
                npx_i = 0;
                npx_currentPattern = PXPAT_PULSE;
            }
        }
        
    }else{
        for(int i=0;i<NUMPIXELS;i++){
            pixelstrip.setPixelColor(i, red);
        }
        pixelstrip.show();
    }
}

