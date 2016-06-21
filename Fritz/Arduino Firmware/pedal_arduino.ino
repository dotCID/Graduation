void setup() {
  // put your setup code here, to run once:
  pinMode(13, OUTPUT);
  pinMode(11, INPUT_PULLUP);
  pinMode(10, INPUT_PULLUP);
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  bool p10State = digitalRead(10);
  bool p11State = digitalRead(11);
  digitalWrite(13, p10State);
  Serial.print("p10: ");
  Serial.println(p10State);
  delay(100);
}
