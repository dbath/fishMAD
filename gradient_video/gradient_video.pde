
import java.io.FileWriter;
import java.io.*;
import java.util.*;
import java.math.BigDecimal;
import java.text.DecimalFormat;
import java.time.Instant;
import java.sql.Timestamp;
import java.util.Collections;
import ketai.net.KetaiNet;


//GUI Setup
boolean goNoGo = true;
boolean finished = false;

//Logging setup
FileWriter fw;
BufferedWriter bw;
DecimalFormat formatter = new DecimalFormat("###.#");



int dotSize = 25;  // size of dots

int nDots = 20;  //number of dots


int t0;
int tLoop;
int loopnum = 0;
float alpha = 100;
int currentEpoch = 0;
int hideMode = 0;
float stopgo = 1.0;
int DIRECTION = 1;
float fadeLength = 0.1;
boolean running = false;
float setSpeed = 1000;
float speed = 1000;
FloatList coherences;
float C;
int myFrameCount = 0;

Dots group1 = new Dots(20,speed,1,100, true);
//Dots group2 = new Dots(3000,0,1,100, true);
//Drawing variables
int sqBar; 

String myIP;
int IPVal;
int [] IPinfo;


void setup(){

  colorMode(HSB, 100,100,100,100);
  size(1280,1280);//fullScreen();
  ellipseMode(CENTER);
  sqBar = 0;//(width - height) /2;
  
  stroke(0,0,0,0);
  fill(55,00,100,100);; 

  C = 1.0; 
  group1.Init();
  group1.Set(int(nDots*(C)), speed, 1);
  t0 = millis();

}


void squareFrame(){
  fill(0,0,0,100);
  rect(0,0,sqBar, height);
  rect(width - sqBar,0,sqBar, height);
}

void hideFrame(float alpha){
  fill(55,0,100,alpha);
  rect(0,0,width, height);
}


public class Dots {
  int NUMBER_OF_THINGS;
  float vel;  // speed and direction of rotation
  float dir;  // make 1 to move (positive for clockwise)
  int COLOUR;
  float fade;
  int myFrameCount;
  boolean RAND;
  Dot[] DotList;
  
  public Dots(int numDots, float _vel,  float _dir, int colour, boolean _RAND) { 
    
    NUMBER_OF_THINGS = numDots; 
    vel =  _vel / 1000.0;
    dir = _dir;
    COLOUR = colour;
    this.RAND = _RAND;
    Init();
  }      
  
  public void Reset(){
    Init();
  }
  
  private void Init() {
    
    //ArrayList<Dot> DotList = new ArrayList<Dot>(NUMBER_OF_THINGS);
    DotList = new Dot[nDots];
    for (int i=0; i< nDots; i++){
      DotList[i] = (new Dot(random(0, TWO_PI), this.vel, this.dir));
    }
  }
  
  void drawGradient(float x, float y, float radius) {
    float h = 1;//colour;
    fill(0,0,0,0);
    for (float r = radius; r > 0; --r) {
      stroke(0,0,0,h);
      ellipse(x, y, r, r);
      h = sqrt(radius-r);//sqrt(h/200);
    }
  }
  void update() { 
    for(int i=0; i < this.NUMBER_OF_THINGS; i++){           //DotList.length; i++){  //for (Dot dot : DotList){
      Dot dot = DotList[i];
      if (this.RAND == true){ dot.randomMotion();}
      else {dot.renew(); }
      drawGradient(dot.X1, dot.Y1, dot.SIZE );
    }
  }
  void Resize(float lowBound, float highBound) { 
    for(int i=0; i < nDots; i++){  //for (Dot dot : DotList){
      DotList[i].Resize(random(lowBound, highBound));
    }
  }
  void startRandom(){
    this.RAND = true;
  }
  void startCoherent(){
    this.RAND = false;
  }
  void Set(int _numDots, float _Vel, float _Dir) {
    NUMBER_OF_THINGS = _numDots;
    vel = _Vel / 1000.0;
    dir = _Dir; 
    for(int i=0; i < _numDots; i++){  //for (Dot dot : DotList){
      DotList[i].setVEL = vel*dir;
      DotList[i].DIR = dir;
    }
    //_Dots.changeArrayLength(_numDots);
    //_Dots.Reset();
  }

}
  
class Dot{
  float X1, Y1, ROTATION, RAD, SIZE;
  float COLOUR, setVEL, VEL, DIR, CX, CY, VAR, XDIR, YDIR;
  
  Dot(float rotation, float vel, float dir) {
    this.SIZE = random(height/10,height/2);
    this.COLOUR = random(100,100);  
    this.CX = width/2;
    this.CY = height/2;
    this.ROTATION = rotation;
    this.setVEL = vel*random(0.3,1.9);
    this.VEL = vel*random(0.3,1.9);
    this.DIR = dir;
    this.X1 = random(0,1.42)*height + sqBar; 
    this.Y1 = random(0,1.42)*height;
    this.VAR = random(0.5, 0.9);
    this.XDIR = random(-1,1);  // component vector
    this.YDIR = sqrt(1 - this.XDIR) * pow(-1.0, int(random(0,100)));   // randomly positive or negative component vector
    this.RAD = sqrt(sq((this.X1 - width/2)) + sq((this.Y1-height/2)));
  }
  
  void randomMotion() {
    
    if (this.setVEL == 0){ this.VEL=0;}
    else {
    this.VEL = this.VEL + (this.setVEL - this.VEL)/(fadeLength*100);
    }
    
    this.RAD = sqrt(sq((this.X1 - width/2)) + sq((this.Y1-height/2)));
    this.X1 = this.X1 + random(0.8,1.2)*this.XDIR*this.VEL;// + random(-0.1,0.1)*speed;
    this.Y1 = this.Y1 + random(0.8,1.2)*this.YDIR*this.VEL;// + random(-0.1,0.1)*speed;
    
    if (this.X1 > (height + this.SIZE + sqBar)) { this.X1 = (0 - this.SIZE + sqBar);}
    else if (this.X1 < (sqBar-this.SIZE)) { this.X1 = (height + this.SIZE + sqBar);}
    if (this.Y1 > height + this.SIZE) { this.Y1 = (0 - this.SIZE);}
    else if (this.Y1 < (0-this.SIZE)) { this.Y1 = (height + this.SIZE);}
  }
  
  void renew() {
    if (this.setVEL == 0){ this.VEL=0;}
    else {
    this.VEL = this.VEL + (this.setVEL - this.VEL)/(fadeLength*100);
    }
    this.ROTATION = this.ROTATION + this.VEL;
    this.X1 = (cos(this.ROTATION)*this.RAD + cos(this.VAR*this.ROTATION)) + this.CX ;
    this.Y1 = (sin(this.ROTATION)*this.RAD + sin(this.VAR*this.ROTATION)) + this.CY ;
  }
  void Resize(float sizeFactor){
    this.SIZE = this.SIZE*sizeFactor;
  }
}


void draw(){   

  background(55,0,100,100);
  group1.update();
  //hideFrame(alpha*hideMode);
  //squareFrame();
  saveFrame("video/stim-######.png");
  
}
void stop() {
}
