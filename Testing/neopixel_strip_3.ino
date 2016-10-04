/**
    Test to check whether NeoPixels and Servos can play nice.
**/

#include <Adafruit_NeoPixel.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define NPX_PIN 6
#define NUMPIXELS 15
#define PXGROUP 5

#define SRV_PIN 3 // position 3 on the shield

#define SERVOMIN  125 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  525 // this is the 'maximum' pulse length count (out of 4096)

Adafruit_PWMServoDriver s_drv = Adafruit_PWMServoDriver();
Adafruit_NeoPixel pixelstrip = Adafruit_NeoPixel(NUMPIXELS, NPX_PIN, NEO_GRB + NEO_KHZ800);

uint32_t red = pixelstrip.Color(255, 0, 0);
uint32_t green = pixelstrip.Color(0, 255, 0);
uint32_t blue = pixelstrip.Color(0, 0, 255);
uint32_t white = pixelstrip.Color(255, 255, 255);
uint32_t none = pixelstrip.Color(0, 0, 0);


uint32_t colours[] = { red,  white, red, green, blue};

void setup(){
    s_drv.begin();
    s_drv.setPWMFreq(60);

    pixelstrip.begin();
    for(int i=0;i<NUMPIXELS;i++){
            pixelstrip.setPixelColor(i, pixelstrip.Color(0, 0, 0));
    }
    pixelstrip.show();
    delay(2000);
}

int c = 0;
int l = 0;

uint16_t pulselen = SERVOMAX;
bool posDir = false;
unsigned long delayTime = millis();

void loop(){
    int j=0;
    while(j<PXGROUP){
        if(pulselen >= SERVOMIN && pulselen <= SERVOMAX){
            s_drv.setPWM(SRV_PIN, 0, pulselen);

            if(posDir){ pulselen+=5; }
            else{ pulselen-=5; };
            
            if(pulselen >= SERVOMAX){
                pulselen = SERVOMAX;
                posDir = false;
            }else if(pulselen <= SERVOMIN){
                pulselen = SERVOMIN;
                posDir = true;
            }
            
            delay(25);
        }
        
        if(millis() - delayTime > 100){
            // turn all off
            for(int i=0;i<NUMPIXELS;i++){
                pixelstrip.setPixelColor(i, pixelstrip.Color(0, 0, 0));
            }
          
            // turn on every 5th one
            for(int i=0;i<NUMPIXELS/PXGROUP;i++){
              if(i!=1){
                pixelstrip.setPixelColor(j+PXGROUP*i, colours[c]);
              }else{
                pixelstrip.setPixelColor(PXGROUP*2-j-1, colours[c]);

              }
            }
            
            pixelstrip.show();
            j++;
            delayTime = millis();
        }
    }
 
    l++;
    if(l % 5 == 0){
      c++;
      if(c>4) c=0;
    }
    
}
