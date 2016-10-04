#include <Adafruit_NeoPixel.h>

#define NPX_PIN 6

#define NUMPIXELS 15

#define PXGROUP 5



Adafruit_NeoPixel pixelstrip = Adafruit_NeoPixel(NUMPIXELS, NPX_PIN, NEO_GRB + NEO_KHZ800);

uint32_t red = pixelstrip.Color(255, 0, 0);
uint32_t green = pixelstrip.Color(0, 255, 0);
uint32_t blue = pixelstrip.Color(0, 0, 255);

uint32_t white = pixelstrip.Color(255, 255, 255);

uint32_t colours[] = {red, green, blue, white};

void setup(){
    pixelstrip.begin();
}

int c = 0;
int l = 0;

void loop(){
    for(int j=0;j<PXGROUP;j++){
      
        // turn all off
        for(int i=0;i<NUMPIXELS;i++){
            pixelstrip.setPixelColor(i, pixelstrip.Color(0, 0, 0));
        }
      
        // turn on every 5th one
        for(int i=0;i<NUMPIXELS/PXGROUP;i++){
            pixelstrip.setPixelColor(j+PXGROUP*i, colours[c]);
        }
        
        pixelstrip.show();

        delay(100);
    }
    l++;
    if(l % 5 == 0){
      c++;
      if(c>3) c=0;
    }
    
}
