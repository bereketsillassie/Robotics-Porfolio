// ESP32 Arduino

/*
Pin map reference:

1 - 32 LRev
2 - 33 RRev
3 - 23 Speed-H
4 - 22 Speed-L
5 - 21 Brake
6 - 21 Brake (shared)
7 - 18 Speed-H
8 - 19 Speed-L

*/

// DACs
#define L_DAC      25
#define R_DAC      26

// Control pins
#define REV_LEFT   32
#define REV_RIGHT  33
#define SP_HIGH    23   
#define SP_LOW     22   
#define BRAKE      21

// Voltage scaling for throttle
const float Vmin    = 0.84;   // controller idle
const float Vmax    = 3.30;   // limited by ESP32 DAC
const float VdacMax = 3.30;

// Variables
int swap = 1;
int count = 0;

void setup() {
  
  pinMode(REV_LEFT, OUTPUT);
  pinMode(REV_RIGHT, OUTPUT);
  pinMode(SP_HIGH, OUTPUT);
  pinMode(SP_LOW, OUTPUT);
  pinMode(BRAKE, OUTPUT);

  // Initialize them LOW 
  digitalWrite(REV_LEFT, LOW);
  digitalWrite(REV_RIGHT, LOW);
  digitalWrite(SP_HIGH, LOW);
  digitalWrite(SP_LOW, LOW);
  digitalWrite(BRAKE, LOW);
  set3Speed(1);
  delay(1000 * 5);  // To prevent one from starting early, Can be solved once the key triggers are wired together
}

// Throttle function
void setThrottle(int dacPin, float duty01) {
  if (duty01 < 0) duty01 = 0;
  if (duty01 > 1) duty01 = 1;
  float v = Vmin + duty01 * (Vmax - Vmin);
  uint8_t code = (uint8_t) round((v / VdacMax) * 255.0f);
  dacWrite(dacPin, code);
}


void set3Speed(int mode){    // mode: 1=Low, 2=High, 3=Mid
  bool H = false, L = false;

  if (mode == 1) {                
    L = true;                     
  } else if (mode == 2) {         
    // both open (H=false, L=false)
  } else if (mode == 3) {         
    H = true;                    
  }

  digitalWrite(SP_HIGH, H ? HIGH : LOW);  
  digitalWrite(SP_LOW,  L ? HIGH : LOW);
}

// Reverse control 
void setReverse(bool leftOn, bool rightOn){
  digitalWrite(REV_LEFT,  leftOn  ? HIGH : LOW);
  digitalWrite(REV_RIGHT, rightOn ? HIGH : LOW);
}

// Brake control 
void setBrake(bool on){
  digitalWrite(BRAKE, on ? HIGH : LOW);
}

void loop() {
  /*
    ------------------- Description -------------------
    This is meant to be an example of how to controll the 
    Motor set up in the Google drive video

    Functions: 
    setBrake: - This is a function that sends a signal to stop the motors
              - This will activate regardless of motion
              - Parameter: bool ( True or False )

    setReverse: - This function will reverse the spin direction of the motors 
                - This will activate regardless of motion 
                - Parameter: Left bool ( True or False ) True reverse & False normal direction
                             Right bool ( True or False )

    set3Speed:  - This will change the max speed/"gearing" settings of the motor 1 (Low), 2 (High), 3 (Mid)
                - This will activate regardless of motion (better if done when not in motion)
                - Parameter: int (1, 2 , or 3)
    
    setThrottle:  - This will change the trottle of the motor
                  - This must be above the Vmin = 0.84 and below the Vmax = 3.30
                  - Can tecnically go to 4.8 v for motor controller but limited by ESP32 3.3 v logic
                  - WARNIGN: Do NOT connect more than 3.3v to this whille connected to ESP32
                  - Parameter: variable (L_DAC or R_DAC), float (0.84 < x < 3.30)
                             
  */

  // Example: canging speed settings
  set3Speed(1);  // Low
  //set3Speed(2);  // High
  //set3Speed(3);  // Mid


  // Example throttle sweep (both sides)
  for (int i=0;i<=100;i++){ 
    setThrottle(L_DAC, i/100.0f); 
    setThrottle(R_DAC, i/100.0f); 
    delay(20); 
  }
  for (int i=100;i>=0;i--){ 
    setThrottle(L_DAC, i/100.0f); 
    setThrottle(R_DAC, i/100.0f); 
    delay(20); 
  }

  

  // Example reverse toggle
  if ((count % 2) == 0){  
    setReverse(true,true);   
  } else {  
    setReverse(false,false); 
  }

  // Example brake activation  
  // setBrake(true);
  // setBrake(false);

  count++;
  delay(500);
}
