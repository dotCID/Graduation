void setup() {
  pinMode(13, OUTPUT);
  // To improve stability, some delaying loop
  for(int i=0;i<3;i++){
    digitalWrite(13, LOW);
    delay(500);
    digitalWrite(13, HIGH);
    delay(500);
  }
  
  pinMode(11, INPUT_PULLUP);
  pinMode(10, INPUT_PULLUP);
  Serial.begin(115200);
  delay(500);
  Serial.println("Setup complete.");
  delay(500);
}

void loop() {
  bool p10State = digitalRead(10);
  bool p11State = digitalRead(11);
  digitalWrite(13, p10State);
  Serial.print("p10: ");
  Serial.println(p10State);
  delay(100);
}
