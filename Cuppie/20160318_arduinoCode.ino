/**
    This sketch reads the serial connection, then actuates the servos as requested within the given limits.
**/

#include <Servo.h>

#define BH_PIN 3
#define BV_PIN 5
#define TH_PIN 6
#define TV_PIN 9

Servo sBH, sBV, sTH, sTV;
double BH_pos,BV_pos,TH_pos, TV_pos;
bool fullPrint = false;
bool fullStop = false;

#define BH_MIN 0
#define BH_MAX 180
#define BH_DEF 94

#define BV_MIN 90
#define BV_MAX 180
#define BV_DEF 155

#define TH_MIN 0
#define TH_MAX 180
#define TH_DEF 98

#define TV_MIN 40
#define TV_MAX 180
#define TV_DEF 145

#define BEAT_TRESHOLD 10

String inputString ="";
bool stringComplete = false;

bool beat = false;
bool beaten = false;
unsigned long beatTime = 0;

void setup(){
    Serial.begin(115200);
    sBH.attach(BH_PIN);
    sBV.attach(BV_PIN);
    sTH.attach(TH_PIN);
    sTV.attach(TV_PIN);
    pinMode(13, OUTPUT);
    
    BH_pos = BH_DEF;
    BV_pos = BV_DEF;
    TH_pos = TH_DEF;
    TV_pos = TV_DEF;
    
    Serial.println(F("Setup done."));
}

void loop(){
    readSerial();
    runMotors();

    if(beat){ 
      digitalWrite(13, HIGH); 
      
      // TODO: REMOVE
      delay(5);
      
      digitalWrite(13, LOW); 
      beat = false; 
    };
   
    
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
            TH_pos = TH_DEF;
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
    }if(inputString.startsWith("TH")){
      String val = inputString.substring(3,inputString.length());
      TH_pos = val.toFloat();
      if(TH_pos<TH_MIN) TH_pos = TH_MIN;
      if(TH_pos>TH_MAX) TH_pos = TH_MAX;
      
      if(fullPrint) Serial.print(F("TH_pos is now "));Serial.println(TH_pos);
    }if(inputString.startsWith("TV")){
      String val = inputString.substring(3,inputString.length());
      TV_pos = val.toFloat();
      if(TV_pos<TV_MIN) TV_pos = TV_MIN;
      if(TV_pos>TV_MAX) TV_pos = TV_MAX;
      
      if(fullPrint) Serial.print(F("TV_pos is now "));Serial.println(TV_pos);
    }if(inputString.startsWith("BEAT")){
      beat = true;
    }
      inputString = "";
      stringComplete = false;
  }
}

/*
    This function moves the servos to the currently set positions if they adhere to the limits.
*/
void runMotors(){
    if(!fullStop){
        if((BH_pos >= BH_MIN) && (BH_pos <= BH_MAX))  sBH.write(BH_pos);
        if((BV_pos >= BV_MIN) && (BV_pos <= BV_MAX))  sBV.write(BV_pos);
        if((TH_pos >= TH_MIN) && (TH_pos <= TH_MAX))  sTH.write(TH_pos);
        if((TV_pos >= TV_MIN) && (TV_pos <= TV_MAX))  sTV.write(TV_pos);
    }else{
        //Serial.print(F("All motion is currently stopped. Please send \"start\" to start moving."));
    }
}

/*
    This function sends a HIGH to the specified pin to react to a beat 
*/
bool beatPin(int pin){
  if(beatTime == 0){
    beatTime = millis();
    digitalWrite(pin, HIGH);
    return true;
  }
  
  if(millis() - beatTime > BEAT_TRESHOLD){ 
       digitalWrite(pin,LOW); 
       beatTime = 0;
       return false;
  }
}
