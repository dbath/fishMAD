import processing.video.*;
import processing.io.*;


// HARDWARE VARIABLES
int progPin = 27;   //indicates the program is running
boolean PROG = true;
int stimPin = 22;  //indicates that a stimulus is running
boolean STIM = false;


// PROTOCOL VARIABLES
int wait = 5; //seconds
int fadeTime = 2000;
boolean makingVideo = true;

// SOFTWARE VARIABLES
int t0;
int t1;
int startTime;


int myDefNum2 = 550;
int myDefNum = 1000 - myDefNum2;
float myDefSpeed = 3;
int myframeCount = 0;

Bars test1 = new Bars(myDefNum, myDefSpeed, -1, 1);
Bars test2 = new Bars(myDefNum2, myDefSpeed, 1, 1);
int w = width/2;
int h = height/2;

void setup() {
  
  fullScreen(2);//size(1900,900);//fullScreen();//size(200, 200);
  noCursor();
  ellipseMode(CENTER);
  GPIO.pinMode(progPin, GPIO.OUTPUT);
  GPIO.digitalWrite(progPin, PROG);
  GPIO.pinMode(stimPin, GPIO.OUTPUT);
  GPIO.digitalWrite(stimPin, STIM);
  

  //randomSeed(10);
  w = width/2;
  h = height/2;
  //frameRate(30);
  colorMode(HSB, 100, 100, 100, 100);
  //background(0,100,100,100);
  stroke(0,0,0,0);
  t0=millis();
  startTime = millis(); 
  test1.Init();
  test2.Init();
  
  
}

void draw() {
  t1 = millis();
  t0 = t1;

  background(0,0,100,100);
  stroke(0,0,0,0);
  fill(0);
  
  test1.update();
  test2.update();
  
  saveFrame();
  
  if (myframeCount > 1200){ exit();}
  
  myframeCount += 1;

}
void Set(Bars _bars, int _numBars, float _Vel, float _Dir) {
  _bars.NUMBER_OF_THINGS = _numBars;
  _bars.vel = _Vel / 1000.0;
  _bars.dir = _Dir;
  //_bars.Reset();
}
public class Bars {
  int NUMBER_OF_THINGS;
  float vel;  // speed and direction of rotation
  float dir;  // make 1 to move (positive for clockwise)
  int COLOUR;
  float fade;
  int myFrameCount;
  Bar[] barList;
  
  public Bars(int numBars, float _vel,  float _dir, int colour) {     
    NUMBER_OF_THINGS = numBars; 
    vel =  _vel / 1000.0;
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
      barList[i].renew(barList[i].ROTATION + vel*dir);

      
      fill(0,100,00,barList[i].COLOUR);
      ellipse(barList[i].X1, barList[i].Y1, barList[i].SIZE, barList[i].SIZE);
      

    }
  }

  
class Bar {
  float X1, Y1, ROTATION, RAD, SIZE;
  float COLOUR,  VEL, DIR;
  float DRIFT;
  
  Bar(float rotation, float vel, float dir) {
    this.SIZE = random(20,40);
    this.COLOUR = random(30,80);  
    this.ROTATION = rotation;
    this.VEL = vel;
    this.DIR = dir;
    this.X1 = randomGaussian()*width/2 + w;
    this.Y1 = randomGaussian()*height/2 + h;
    this.RAD = sqrt(sq((this.X1 - w)) + sq((this.Y1-h)));
    this.DRIFT = random(-0.2,0.2);
  }
  
  void renew(float rotation) {
    this.X1 = (cos(rotation)*this.RAD) - 0.5*this.SIZE + w;
    this.Y1 = (sin(rotation)*this.RAD) - 0.5*this.SIZE + h;
    this.ROTATION = rotation;
    this.RAD = this.RAD + this.DRIFT;
    if (this.RAD < 100.0 ){ this.DRIFT = this.DRIFT * -1.0; }
    if (this.RAD > width/2 ){ this.DRIFT = this.DRIFT * -1.0; }
    
    
  }
}
}