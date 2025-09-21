#include <queue>
#include <vector>
#include <algorithm>
using namespace std;

// === ENCODER & ROBOT SETTINGS ===
#define ENCODER_LEFT_A 34
#define ENCODER_LEFT_B 35
#define ENCODER_RIGHT_A 32
#define ENCODER_RIGHT_B 33

#define PPR 882  // pulses per revolution of output shaft
#define WHEEL_DIAMETER 35.0  // mm
#define PI 3.1416
float wheelCircumference = PI * WHEEL_DIAMETER;
float mm_per_pulse = wheelCircumference / PPR;

#define CELL_SIZE_MM 180  // Maze square size in mm
#define ROBOT_WIDTH_MM 105   // Distance between wheels 
#define TURN_90_DISTANCE (PI * ROBOT_WIDTH_MM / 4.0)


// === MOTOR DRIVER PINS===
#define AIN1 25
#define AIN2 26
#define PWMA 27  // Left motor PWM

#define BIN1 14
#define BIN2 12
#define PWMB 13  // Right motor PWM

// === Maze Constants ===
#define MAZE_SIZE 10
#define NORTH 0
#define EAST 1
#define SOUTH 2
#define WEST 3

// ===  DIGITAL SENSOR PINS ===
#define SENSOR_LEFT  19
#define SENSOR_FRONT 18
#define SENSOR_RIGHT 5

// Directions for row/column deltas
const int dRow[] = {-1, 0, 1, 0};
const int dCol[] = { 0, 1, 0, -1};


// === PD Constants ===
float Kp = 1.5, Kd = 0.1;

// === Maze Cell Structure ===
struct Cell {
  bool wall[4];     // N, E, S, W
  bool visited;
  int distance;
};

// Maze Grid
Cell maze[MAZE_SIZE][MAZE_SIZE];

// Robot State
int robotRow = 9;
int robotCol = 0;
int robotDir = NORTH;

// === ENCODER & PID VARIABLES ===
volatile long totalLeftCount = 0;
volatile long totalRightCount = 0;

volatile int leftCount = 0;
volatile int rightCount = 0;

float targetRPM_L = 0, targetRPM_R = 0;
float leftRPM = 0, rightRPM = 0;

float error_L = 0, prevError_L = 0;
float error_R = 0, prevError_R = 0;

unsigned long lastTime = 0;

// === INTERRUPT HANDLERS for ENCODERS===
void IRAM_ATTR leftEncoderISR() {
  if (digitalRead(ENCODER_LEFT_A) == digitalRead(ENCODER_LEFT_B))
    totalLeftCount++;
  else
    totalLeftCount--;
  leftCount++;
}

void IRAM_ATTR rightEncoderISR() {
  if (digitalRead(ENCODER_RIGHT_A) == digitalRead(ENCODER_RIGHT_B))
    totalRightCount++;
  else
    totalRightCount--;
  rightCount++;
}



// === Initialize Maze with Unknown Walls ===
void initMaze() {
  for (int r = 0; r < MAZE_SIZE; r++) {
    for (int c = 0; c < MAZE_SIZE; c++) {
      for (int d = 0; d < 4; d++) {
        maze[r][c].wall[d] = true;  
      }
      maze[r][c].distance = 9999;
    }
  }
}

// === Center Goal Check ===
bool isCenter(int row, int col) {
  return (row == 4 || row == 5) && (col == 4 || col == 5);
}



// === A* Algorithm Functions ===

// === Heuristic: Euclidean distance ===
float heuristic(int r, int c) {
  // Euclidean distance from curr to goal cell
  float minH = 1e9;
  for (int gr = 4; gr <= 5; gr++) {
    for (int gc = 4; gc <= 5; gc++) {
      float dr = r - gr;
      float dc = c - gc;
      float h = sqrt(dr*dr + dc*dc);
      if (h < minH) minH = h;
    }
  }
  return minH;
}

// === A* path planning ===
vector<pair<int,int>> aStarPlan(int startR, int startC) {
  const float INF = numeric_limits<float>::infinity();

  static float g[MAZE_SIZE][MAZE_SIZE];
  static float f[MAZE_SIZE][MAZE_SIZE];
  static bool  closed[MAZE_SIZE][MAZE_SIZE];
  static int   parentR[MAZE_SIZE][MAZE_SIZE];
  static int   parentC[MAZE_SIZE][MAZE_SIZE];

  for (int r=0; r<MAZE_SIZE; r++) {
    for (int c=0; c<MAZE_SIZE; c++) {
      g[r][c] = 1e10;
      f[r][c] = 1e10;
      closed[r][c] = false;
      parentR[r][c] = -1;
      parentC[r][c] = -1;
    }
  }

  struct PQNode {
    int r, c;
    float g, f;
  };
  struct Cmp {
    bool operator()(const PQNode& a, const PQNode& b) const {
      return a.f > b.f; 
    }
  };
  priority_queue<PQNode, vector<PQNode>, Cmp> open;

  g[startR][startC] = 0.0f;
  f[startR][startC] = heuristic(startR, startC);
  open.push({startR, startC, g[startR][startC], f[startR][startC]});
  int goalR = -1, goalC = -1;

  while (!open.empty()) {
    PQNode cur = open.top();
    open.pop();

    if (closed[cur.r][cur.c]) continue;
    closed[cur.r][cur.c] = true;

    if (isCenter(cur.r, cur.c)) {
      goalR = cur.r; goalC = cur.c;
      break;
    }

    for (int dir = 0; dir < 4; dir++) {
      int nr = cur.r + dRow[dir];
      int nc = cur.c + dCol[dir];
      int opposite = (dir + 2) % 4;

      if (nr < 0 || nr >= MAZE_SIZE || nc < 0 || nc >= MAZE_SIZE) continue;

      
      if (maze[cur.r][cur.c].wall[dir]) continue;

      if (closed[nr][nc]) continue;

      float gNew = g[cur.r][cur.c] + 1.0f;  
      if (gNew < g[nr][nc]) {
        g[nr][nc] = gNew;
        f[nr][nc] = gNew + heuristic(nr, nc);
        parentR[nr][nc] = cur.r;
        parentC[nr][nc] = cur.c;
        open.push({nr, nc, g[nr][nc], f[nr][nc]});
      }
    }
  }

  vector<pair<int,int>> path;
  if (goalR == -1) return path; 

 
  int r = goalR, c = goalC;
  while (!(r == startR && c == startC)) {
    path.push_back({r, c});
    int pr = parentR[r][c];
    int pc = parentC[r][c];
    if (pr == -1 || pc == -1) { path.clear(); return path; }
    r = pr; c = pc;
  }
  reverse(path.begin(), path.end());
  return path;
}

void navigateToCenter() {
  while (!isCenter(robotRow, robotCol)) {
    // Step 1: Sense/update walls for current cell
    updateWallsFromSensors();

    // Step 2: Plan with current knowledge
    vector<pair<int,int>> path = aStarPlan(robotRow, robotCol);
    if (path.empty()) {
      break;
    }

    // Step 3: Execute  first step then replan next loop
    int nextRow = path[0].first;
    int nextCol = path[0].second;

    int dir = -1;
    for (int d = 0; d < 4; d++) {
      if (robotRow + dRow[d] == nextRow && robotCol + dCol[d] == nextCol) {
        dir = d; break;
      }
    }
    if (dir == -1) {
      Serial.println("Error1");
      break;
    }
    move(dir);
  }
  Serial.println("Goal reached");
}

// === Movement code ===
void move(int direction) {
  int turn = (direction - robotDir + 4) % 4;
  if (turn == 1) turnRight90(50);
  else if (turn == 3) turnLeft90(50);
  else if (turn == 2) { turnLeft90(50); turnLeft90(50); }

  moveForwardOneCell(50);
  robotDir = direction;
  robotRow += dRow[robotDir];
  robotCol += dCol[robotDir];
}

// === Robot Movement Functions ===
void updatePD() {
  unsigned long currentTime = millis();
  if (currentTime - lastTime >= 100) {
    float dt = (currentTime - lastTime) / 1000.0;
    lastTime = currentTime;

    leftRPM = (leftCount / (float)PPR) * 60.0 / dt;
    rightRPM = (rightCount / (float)PPR) * 60.0 / dt;
    leftCount = 0;
    rightCount = 0;

    error_L = targetRPM_L - leftRPM;
    error_R = targetRPM_R - rightRPM;

    float dL = (error_L - prevError_L) / dt;
    float dR = (error_R - prevError_R) / dt;

    float outL = constrain(Kp * error_L + Kd * dL, 0, 255);
    float outR = constrain(Kp * error_R + Kd * dR, 0, 255);

    prevError_L = error_L;
    prevError_R = error_R;

    setMotorPower(PWMA, AIN1, AIN2, outL, targetRPM_L >= 0);
    setMotorPower(PWMB, BIN1, BIN2, outR, targetRPM_R >= 0);
  }
}

// === MOVE FORWARD ONE CELL ===
void moveForwardOneCell(float speedRPM) {
  totalLeftCount = 0;
  totalRightCount = 0;
  targetRPM_L = speedRPM;
  targetRPM_R = speedRPM;

  while (true) {
    updatePD();
    float distL = totalLeftCount * mm_per_pulse;
    float distR = totalRightCount * mm_per_pulse;
    if ((distL + distR) / 2.0 >= CELL_SIZE_MM) break;
  }
  setMotorPower(PWMA, AIN1, AIN2, 0, true);
  setMotorPower(PWMB, BIN1, BIN2, 0, true);
}

// === TURN LEFT 90 ===
void turnLeft90(float speedRPM) {
  totalLeftCount = 0;
  totalRightCount = 0;
  targetRPM_L = -speedRPM;
  targetRPM_R = speedRPM;

  while (true) {
    updatePD();
    float dist = ((abs(totalLeftCount) + abs(totalRightCount)) / 2.0) * mm_per_pulse;
    if (dist >= TURN_90_DISTANCE) break;
  }
  setMotorPower(PWMA, AIN1, AIN2, 0, true);
  setMotorPower(PWMB, BIN1, BIN2, 0, true);
}

// === TURN RIGHT 90 ===
void turnRight90(float speedRPM) {
  totalLeftCount = 0;
  totalRightCount = 0;
  targetRPM_L = speedRPM;
  targetRPM_R = -speedRPM;

  while (true) {
    updatePD();
    float dist = ((abs(totalLeftCount) + abs(totalRightCount)) / 2.0) * mm_per_pulse;
    if (dist >= TURN_90_DISTANCE) break;
  }
  setMotorPower(PWMA, AIN1, AIN2, 0, true);
  setMotorPower(PWMB, BIN1, BIN2, 0, true);
}

// === MOTOR DRIVE FUNCTION ===
void setMotorPower(int pwmPin, int in1, int in2, int speed, bool forward) {
  digitalWrite(in1, forward ? HIGH : LOW);
  digitalWrite(in2, forward ? LOW : HIGH);
  analogWrite(pwmPin, speed);
}


// === SENSOR INFO FUNCTION ===
void updateWallsFromSensors() {
  bool leftWall   = digitalRead(SENSOR_LEFT);
  bool frontWall  = digitalRead(SENSOR_FRONT);
  bool rightWall  = digitalRead(SENSOR_RIGHT);

  // Update current cell walls relative to current direction
  maze[robotRow][robotCol].wall[robotDir] = frontWall;
  maze[robotRow][robotCol].wall[(robotDir + 3) % 4] = leftWall;
  maze[robotRow][robotCol].wall[(robotDir + 1) % 4] = rightWall;

  // Also update the neighbor cell opposite walls if they are in bounds
  int frontRow = robotRow + dRow[robotDir];
  int frontCol = robotCol + dCol[robotDir];
  if (frontRow >= 0 && frontRow < MAZE_SIZE && frontCol >= 0 && frontCol < MAZE_SIZE)
    maze[frontRow][frontCol].wall[(robotDir + 2) % 4] = frontWall;

  int leftDir = (robotDir + 3) % 4;
  int leftRow = robotRow + dRow[leftDir];
  int leftCol = robotCol + dCol[leftDir];
  if (leftRow >= 0 && leftRow < MAZE_SIZE && leftCol >= 0 && leftCol < MAZE_SIZE)
    maze[leftRow][leftCol].wall[(leftDir + 2) % 4] = leftWall;

  int rightDir = (robotDir + 1) % 4;
  int rightRow = robotRow + dRow[rightDir];
  int rightCol = robotCol + dCol[rightDir];
  if (rightRow >= 0 && rightRow < MAZE_SIZE && rightCol >= 0 && rightCol < MAZE_SIZE)
    maze[rightRow][rightCol].wall[(rightDir + 2) % 4] = rightWall;
}


// === MAIN SETUP ===
void setup() {
  Serial.begin(115200);

  pinMode(ENCODER_LEFT_A, INPUT);
  pinMode(ENCODER_LEFT_B, INPUT);
  pinMode(ENCODER_RIGHT_A, INPUT);
  pinMode(ENCODER_RIGHT_B, INPUT);

  attachInterrupt(ENCODER_LEFT_A, leftEncoderISR, CHANGE);
  attachInterrupt(ENCODER_RIGHT_A, rightEncoderISR, CHANGE);


  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);

  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);

  pinMode(SENSOR_LEFT, INPUT);
  pinMode(SENSOR_FRONT, INPUT);
  pinMode(SENSOR_RIGHT, INPUT);

  lastTime = millis();
  
 
  initMaze();
  updateWallsFromSensors();
  navigateToCenter();

  // Begin 
}

void loop() {
  // wont be looping
}
