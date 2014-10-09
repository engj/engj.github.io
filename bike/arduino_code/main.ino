#include <ADXL345.h>
#include <bma180.h>
#include <HMC58X3.h>
#include <ITG3200.h>
#include <MS561101BA.h>
#include <I2Cdev.h>
#include <MPU60X0.h>
#include <EEPROM.h>
#include "DebugUtils.h"
#include "CommunicationUtils.h"
#include "FreeIMU.h"
#include <FlexiTimer2.h>
#include <Wire.h>
#include <SPI.h>
#include <Servo.h>
#include "Arduino.h"
#include <digitalWriteFast.h>

#define BUFLEN         30

// Motor Control constants
#define interruptA      0
#define DELAY          10
#define MSTOS   1000000.0

// Sliding Mode Parameters
#define smcETA        3.5
#define smcLAMBDA      20
#define samplingTime 0.05 // Seconds
#define sinLambda  0.9877
#define cosLambda  0.1564

// Bike model parameters
volatile const float b = 0.254;   // Wheelbase
volatile const float m = 1.06;   // Mass 
volatile const float a = 0.1566;  // Horizontal Dist from CM to Rear Wheel
volatile const float h = 0.16;   // Height of CM
volatile const float c = 0.0078;      // Trail of Front Wheel
volatile const float D = 0.0055; // negative of Product of Inertia (xz)
volatile const float J = 0.02606;// Moment of Inertia (xx)
volatile const float V = 1;


// SMC parameters
volatile const float commonDenom = J*((V*V*sinLambda)-(b*9.81*cosLambda)); 
volatile const float a1          = -D*V*9.81/commonDenom;
volatile const float a2          = -m*9.81*9.81*(b*h*cosLambda-a*c*sinLambda)/commonDenom;
volatile const float b1          = D*V*b/(a*c*m*commonDenom);
volatile const float b2          = b*(V*V*h - a*c*9.81)/(a*c*commonDenom);
volatile const float TorqCons    = -m*a*c*9.81*sinLambda/b;


// Controller IO variables
Servo myservo;  // Servo object
float angles[3]; // Yaw Pitch Roll of the bike
volatile float phiDes; // Desired Lean Angle
float sensorValues[6]; // Sensor Values for Acceleration and Angular Rates, offsets taken into account
float angularRates[3]; // Sensor Angular rates, offsets taken into account
volatile float motorSpeed; // Duty Cycle
volatile float DelF; // Controlled Actuation
volatile float servoPos; // Controlled Input to the Servo
volatile float phi; // Lean Angle
volatile float phiDot; // Lean Rate
volatile float prevDelF; // Previous Lean Rate

// Network Variables
unsigned int controlMode;

// Set the FreeIMU object
FreeIMU my6IMU = FreeIMU();

void setup() { 
    
  // Default Network Variables
  controlMode = 0;
  
  
  // Initialize Controller Variables
  servoPos = 0;
  motorSpeed = 0;
  
  // Connect servo to pin 9
  myservo.attach(9);
  delay(5);
  
  // Initialize Serial Comm  
  Serial.begin(115200); //Baud Rate
  Wire.begin();
  delay(5);
  
  // Initialize IMU  
  my6IMU.init(true); // the parameter enable or disable fast mode
  delay(5);
  
  // Connect Motor to Pin 5
  pinMode(5,OUTPUT);
  delay(5);
  
  
  FlexiTimer2::set(samplingTime * 1000, 1.0 / 1000, runSMC);
  FlexiTimer2::start();
}

void loop() { 
  // Get phiDes and set controlMode
  pullData();
  
  // Get current State
  getCurrState();
  
  // Set Motorspeed
  motorSpeed = 191;
  
  // Code to kill motor and servo if falls
  if (abs(phi) > 1.2){
     servoPos = 90;
     motorSpeed = 0;
  }
  
  // Actuate Servo and Motor
  analogWrite(5, motorSpeed);
}

// Read incoming data from the Serial Port ---------------------------------------------------------------------
void pullData(){
  while(Serial.available() > 0){
      char next = Serial.read();
      if (next == 'R') {
        if(Serial.read() == '{'){
          phiDes = Serial.parseFloat();
        }
      }
      if (next == 'M') {
        if (Serial.read() == '{') {
          controlMode = Serial.parseInt(); 
        }
      }  
    }
    
    if (controlMode == 0) {
      phiDes = 0;
    }
}


// Obtain the current State of the Bike ------------------------------------------------------------------------
void getCurrState() {
  my6IMU.getYawPitchRollRad(angles);
  my6IMU.getValues(sensorValues);
  
  int i = 3;
  while (i<6){
    angularRates[(i-3)] = sensorValues[i];
    i++;
  }
  
  phiDot = (angularRates[2]+0.12)/57.296; // Convert Lean Angle Rate to rad/s
  phi = angles[1]+0.45; // Lean Angle
}



// Run the Sliding Mode Controller ------------------------------------------------------------------------
void runSMC(){
  DelF = (b1*TorqCons*prevDelF/samplingTime) - (-a1-smcLAMBDA*smcETA)*(phi-0.15-(phiDes/57.296)) + (-a2-smcETA-smcLAMBDA)*phiDot;
  DelF = DelF/(TorqCons*(b1+b2));
  
  // Store History of Steer Angles
  prevDelF = DelF;
  
  servoPos = (unsigned int)( 90 + DelF*57.296 );

  // Limit Servo Input
  if (servoPos > 135){ 
    servoPos = 135;
  }
  if (servoPos < 45){
    servoPos = 45;
  }
  pushData();
  myservo.write(servoPos);
}


// Send Serial Data to the Beaglebone in the form 'PHI{__}DEL{__}BAT{__}' -------------------------------------
void pushData(){
  Serial.print("PHI{");
  Serial.print((int)(phi*57.296)); // Degrees
  Serial.print("}DEL{");
  Serial.print(servoPos); // Degrees
  Serial.println("}BAT{36}");
}
  
  
