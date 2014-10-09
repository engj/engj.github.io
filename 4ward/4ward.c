// Max/min position = 1023/0
// motor1 pins
int motor1_positionPin = 5;
int motor1_speedPin = 3;
int motor1_pinA = 6;
int motor1_pinB = 7;
int motor1_desiredPosition = 0;

// motor2 pins (hasn't been connected so we don't know what the pin numbers are going to be)
int motor2_positionPin = 4;
int motor2_speedPin = 5;
int motor2_pinA = 8;
int motor2_pinB = 9;
int motor2_desiredPosition = 0;

// encoder pins
int encoder_pinA = 10;
int encoder_pinB = 11;
int encoder_pos = 0;
int encoder_pinALast = LOW;
int encoder_n = LOW;
int encoder_previousPosition = 0;
int encoder_previousTime = 0;

// reed switch pin
int Sensor_Pin  =  2;

void setup() {  
  // motor1 setup
  pinMode(motor1_speedPin,OUTPUT);
  pinMode(motor1_pinA, OUTPUT);
  pinMode(motor1_pinB, OUTPUT);
  
  // motor2 setup
  pinMode(motor2_speedPin, OUTPUT);
  pinMode(motor2_pinA, OUTPUT);
  pinMode(motor2_pinB, OUTPUT);
  
  // encoder setup
  pinMode(encoder_pinA, INPUT);
  pinMode(encoder_pinB, INPUT);
  
  // reed switch setup
  pinMode(Sensor_Pin, INPUT);
  
  Serial.begin(9600);
}

void loop() {
  // get the current velocity
  float velocity = getVelocity();
  
  // int velocity = 0; make negative velocity positive
  if (velocity < 0) {
    velocity = -1 * velocity;
  }
  
  if (velocity > 120) {
    motor1_desiredPosition =  117;
    motor2_desiredPosition = 790;
  } else if (velocity > 80) {
    motor1_desiredPosition = 300;
    motor2_desiredPosition = 580;
  } else if (velocity > 40) {
    motor1_desiredPosition = 460;
    motor2_desiredPosition = 400; 
  } else {
    motor1_desiredPosition = 600;
    motor2_desiredPosition = 117;
  }
  
  // make sure desired positions are not outside the limits
  if (motor1_desiredPosition > 600) {
    motor1_desiredPosition = 600;
  } else if (motor1_desiredPosition < 117) {
    motor1_desiredPosition = 117;
  }
  
  if (motor2_desiredPosition > 790) {
    motor2_desiredPosition = 790;
  } else if (motor2_desiredPosition < 117) {
    motor2_desiredPosition = 117;
  }
  
  // move motor1 to motor1_desiredPosition and motor2 to motor2_desiredPosition
  int motor1_currentPosition = analogRead(motor1_positionPin);
  moveMotor1(motor1_currentPosition);
  
  int motor2_currentPosition = analogRead(motor2_positionPin);
  moveMotor2(motor2_currentPosition);
}

float getVelocity() {
  float velocity = 0;
  int val = 0;
  int previousTime = 0;
  int threshold = 500; // at least 500 ms elapsed per revolution
  int currentTime = 0;
  int diameter = 26;
  
  while (velocity  ==  0) {
    val = digitalRead(Sensor_Pin);
    if (val  ==  HIGH) {
      currentTime  =  millis();
      if (previousTime  =  =  0) {
        previousTime  =  currentTime;
        delay(threshold);
      } else {
        velocity  =  (3.142 * diameter) / (currentTime - previousTime); 
      }
    }
  }
  return velocity * 1000;
}

void moveMotor1(int currentPosition){
  analogWrite(motor1_speedPin, 255);
  while (abs(currentPosition - motor1_desiredPosition) > 10) {
    if (currentPosition < motor1_desiredPosition){
      motor1_extend();
    } else {
      motor1_retract();
    }
    currentPosition  =  analogRead(motor1_positionPin);
  } 
  motor1_stop();
}

void motor1_stop(){
  digitalWrite(motor1_pinA, HIGH);
  digitalWrite(motor1_pinB, LOW);
}

void motor1_retract(){
  digitalWrite(motor1_pinA, LOW);
  digitalWrite(motor1_pinB, HIGH);
}

void motor1_stop(){
  digitalWrite(motor1_pinA, LOW);
  digitalWrite(motor1_pinB, LOW);
  analogWrite(motor1_speedPin, 0);
}

void moveMotor2(int currentPosition){
  analogWrite(motor2_speedPin, 255);
  while (abs(currentPosition - motor2_desiredPosition) > 10) {
    if (currentPosition < motor2_desiredPosition){
      motor2_extend();
    } else {
      motor2_retract();
    }
    currentPosition = analogRead(motor2_positionPin);
  } 
  motor2_stop();
}

void motor2_extend(){
  digitalWrite(motor2_pinA, HIGH);
  digitalWrite(motor2_pinB, LOW);
}

void motor2_retract(){
  digitalWrite(motor2_pinA, LOW);
  digitalWrite(motor2_pinB, HIGH);
}

void motor2_stop(){
  digitalWrite(motor2_pinA, LOW);
  digitalWrite(motor2_pinB, LOW);
  analogWrite(motor2_speedPin, 0);
}