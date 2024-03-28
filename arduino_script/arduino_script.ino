int LED_0_PIN = 13;
int LED_1_PIN = 12;
int LED_2_PIN = 11;
const int ON = 1;
const int OFF = 2;

void turnLed(int ledNumber, int operation){
  int signalOfLed;
  if (operation == ON){
    signalOfLed = HIGH;
  }else if(operation == OFF){
    signalOfLed = LOW; 
  }
  switch(ledNumber){
    case 0:
      digitalWrite(LED_0_PIN, signalOfLed);
      break;
    case 1:
      digitalWrite(LED_1_PIN, signalOfLed);
      break;
    case 2:
      digitalWrite(LED_2_PIN, signalOfLed);
      break;
    default:
      break;
  }   
}

void turnOnAllLeds(){
  turnLed(0, ON);
  turnLed(1, ON);
  turnLed(2, ON);
}

void turnOffAllLeds(){
  turnLed(0, OFF);
  turnLed(1, OFF);
  turnLed(2, OFF);
}
void setup() {
  // For sensor:
  Serial.begin(9600);
  //For LEDs
  pinMode(LED_0_PIN, OUTPUT);
  pinMode(LED_1_PIN, OUTPUT);
  pinMode(LED_2_PIN, OUTPUT);
}


void loop() {
  // put your main code here, to run repeatedly:
  int sensorValue = analogRead(A0);
  String ask = Serial.readString();
  if (ask == "0"){
    Serial.println(sensorValue);
  }
  if (ask == "1"){
    turnOnAllLeds();
  }
  if (ask == "2"){
    turnOffAllLeds();  
  }
  
  delay(50);

  if (ask.length() == 3){
      int ledNumber = ask[0]-'0';
      int operation = ask[2] - '0';

      turnLed(ledNumber, operation);
  }
  
}
