#include <Braccio.h> 
#include <Servo.h>
#include <SPI.h>
#include <SD.h>

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;

int incomingByte = 0;   // Variable to store incoming serial data

void setup() {    
  
  //Initialization functions and set up the initial position for Braccio
  //All the servo motors will be positioned in the "safety" position:
  //Base (M1):90 degrees
  //Shoulder (M2): 45 degrees
  //Elbow (M3): 180 degrees
  //Wrist vertical (M4): 180 degrees
  //Wrist rotation (M5): 90 degrees
  //gripper (M6): 10 degrees  
  
  Braccio.begin(SOFT_START_DISABLED); 
  
  Serial.begin(9600);     // opens serial port to receive data from the raspberry pi - python 

}


// Continuous loop in Aruduino
void loop() {

  Serial.println("Entering loop");
  
  // Variable to store data coming in
  String inString = "";    
   
  // If there's new data in coming from the serial port 
  if (Serial.available()) {

    Serial.println("Serial.available() > 0"); 

    // Read the data coming from the serial port
    int inChar = Serial.read();
    Serial.println(inChar);   

    // Control robotic arm to 
    PickupWorkpiece(inChar);
    
  }  

  // Only check for data every 2 seconds 
   delay(2000);
}





// Control the robotic arm to pickup the workpiece
void PickupWorkpiece(int mode){

  // Initialise robotic arm
  digitalWrite(SOFT_START_CONTROL_PIN, HIGH);

  
  // Move to neutral position 
  if(mode==0)
  {
    //(step delay, M1, M2, M3,  M4,  M5,  M6);
    Braccio.ServoMovement(20,   97, 90, 0,  180,  82,   10);   
    delay(1000);
  }


  // Pickup and put in green box
  else if(mode==1)
  {
 
    Braccio.ServoMovement(20,   60, 52, 15,  147,   85,   10);  //up right
    delay(2000);
    
    Braccio.ServoMovement(20,   97, 52, 15,  147,   85,   10);  //up right
    delay(2000);
                    
    Braccio.ServoMovement(20,   97, 56, 0,   147, 85,  10);     //down close  
    delay(2000);
    
    Braccio.ServoMovement(20,   97, 56, 0,   147, 85,  45);     //grip
    delay(2000);   
    
    Braccio.ServoMovement(20,   97, 52, 15,  147,   85,   45);   //lift
    delay(2000); 
    
    Braccio.ServoMovement(20,   135, 52, 15,  147,   85,   45);   //move to right
    delay(2000);
    
    Braccio.ServoMovement(20,   135, 52, 15,  147, 85,   10);   //release
    delay(2000);
    
  }


  // Pickup and put in yellow box
  else if(mode==2)
  {    
    Braccio.ServoMovement(20,   60, 52, 15,  147,   85,   10);  //up right
    delay(2000);
    
    Braccio.ServoMovement(20,   97, 52, 15,  147,   85,   10);  //up right
    delay(2000);
      
    Braccio.ServoMovement(20,   97, 56, 0,   147, 85,  10);      //down close  
    delay(2000);
    
    Braccio.ServoMovement(20,   97, 56, 0,   147, 85,  45);     //grip
    delay(2000);   
    
    Braccio.ServoMovement(20,   97, 52, 15,  147,   85,   45);   //lift
    delay(2000); 
    
    Braccio.ServoMovement(20,   45, 52, 15,  147,   85,   45);   //move to right
    delay(2000);
    
    Braccio.ServoMovement(20,   45, 52, 15,  147, 85,   10);   //release
    delay(2000);
    
  }
}
