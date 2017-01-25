import processing.io.*;

// HARDWARE VARIABLES
int progPin = 27;   //indicates the program is running
boolean PROG = true;
int stimPin = 22;  //indicates that a stimulus is running
boolean STIM = false;


// PROTOCOL VARIABLES
int wait = 2*60*1000;
int fadeTime = 1;

// SOFTWARE VARIABLES
int t0;
int t1;
int startTime;
int tick;
int counter = 0;
int alpha = 0;
int myDefNum = 900;
float myDefSpeed = 0.05;

Bars test1 = new Bars(myDefNum, myDefSpeed, 1, 200);
Bars test2 = new Bars(100, 0.05, 1, 100);
int w = width/2;
int h = height/2;

void setup() {
  fullScreen();//size(700,600);//fullScreen();//size(200, 200);
  noCursor();
  
  GPIO.pinMode(progPin, GPIO.OUTPUT);
  GPIO.digitalWrite(progPin, PROG);
  GPIO.pinMode(stimPin, GPIO.OUTPUT);
  GPIO.digitalWrite(stimPin, STIM);
  
  
  w = width/2;
  h = height/2;
  //frameRate(30);
  colorMode(HSB, 100, 100, 100, 100);
  background(100);
  stroke(0,0,0,0);
  tick=1;
  t0=millis();
  startTime = millis(); 
  test1.Init();
  test2.Init();
}

void draw() {
  t1 = millis();
  t0 = t1;
  if(t1 - startTime >= wait){
    tick = -1*tick;
    startTime = t1;
    STIM = !STIM;
    GPIO.digitalWrite(stimPin, STIM);
    if (counter == 0) { Set(test1, myDefNum, myDefSpeed, 1);}
    if (counter == 2) { Set(test1, myDefNum, myDefSpeed, -1);} 
    if (counter == 4) { Set(test1, myDefNum, myDefSpeed, 1);} 
    if (counter == 6) { Set(test1, myDefNum, myDefSpeed, -1);} 
    
    counter = counter + 1;
  }
  
  background(100);
  stroke(0,0,0,0);
  fill(0);
  
  
  test1.update();
  test2.update();
   
  int timeLeft = wait - (t1 - startTime);
  if (timeLeft <=fadeTime) {
    alpha = (int)((fadeTime - timeLeft)/(fadeTime/100.0));
  }
  else if ((t1 - startTime) <= fadeTime){
    alpha = (int)((fadeTime-(t1-startTime))/(fadeTime/100.0));
  }
  else { 
    alpha = 0;
  }
  //fill(100,0,50, alpha);
  //rect(0,0,width,height);
  fill(0,0,0,100);
  rect(0,0,0.2*width, height);
  rect(0.8*width, 0, 0.2*width, height);
  
}
void Set(Bars _bars, int _numBars, float _Vel, int _Dir) {
  _bars.NUMBER_OF_THINGS = _numBars;
  _bars.vel = _Vel;
  _bars.dir = _Dir;
  //_bars.Reset();
}
public class Bars {
  int NUMBER_OF_THINGS;
  float vel;  // speed and direction of rotation
  int dir;  // make 1 to move (positive for clockwise)
  int COLOUR;
  float fade;
  int myFrameCount;
  Bar[] barList;
  
  public Bars(int numBars, float _vel,  int _dir, int colour) {     
    NUMBER_OF_THINGS = numBars; 
    vel = _vel;
    dir = _dir;
    COLOUR = colour;
    Init();
  }      
  
  
  public void Reset(){
    Init();
  }
  
  private void Init() {
    barList = new Bar[NUMBER_OF_THINGS];
    for (int i=0; i< barList.length; i++){
      float rotation = random(0, TWO_PI);//i* TWO_PI / (NUMBER_OF_THINGS);
      barList[i] = new Bar(rotation,  vel, dir);
    }
  }
  void update() { 
    for (int i=0; i< NUMBER_OF_THINGS; i++){
      if (tick < 0){
        barList[i].renew(barList[i].ROTATION + barList[i].VEL*dir);
      }
      
      fill(0,0,0,barList[i].COLOUR);
      ellipse(barList[i].X1, barList[i].Y1, barList[i].SIZE, barList[i].SIZE);
      

    }
  }

  
class Bar {
  float X1, Y1, ROTATION, RAD, SIZE;
  float COLOUR,  VEL, DIR;
  
  Bar(float rotation, float vel, int dir) {
    this.SIZE = random(10,50);
    this.COLOUR = random(80,100);  
    this.ROTATION = rotation;
    this.VEL = vel;
    this.DIR = dir;
    this.X1 = random(0,width);
    this.Y1 = random(0,height);
    this.RAD = sqrt(sq((this.X1 - w)) + sq((this.Y1-h)));
  }
  
  void renew(float rotation) {
    this.X1 = (cos(rotation)*this.RAD) - 0.5*this.SIZE + w;
    this.Y1 = (sin(rotation)*this.RAD) - 0.5*this.SIZE + h;
    this.ROTATION = rotation;
  }
}
}