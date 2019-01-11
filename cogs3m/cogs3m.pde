
import java.io.FileWriter;
import java.io.*;
import java.util.*;
import java.math.BigDecimal;
import java.text.DecimalFormat;
import java.time.Instant;
import java.sql.Timestamp;
import java.util.Collections;
import ketai.net.KetaiNet;
import spout.*;
Spout spout;

// PImage keeps alpha channel intact, unlike other drawing methods in Processing
PGraphics data;

//GUI Setup

import controlP5.*;
ControlP5 cP5;
Slider abc;
boolean goNoGo = false;
boolean finished = false;

//Logging setup
FileWriter fw;
BufferedWriter bw;
DecimalFormat formatter = new DecimalFormat("###.#");



int dotSize = 1;  // size of dots

int nDots = 200;  //number of dots
int nDotsSlider;

int t0;
int tLoop;
int loopnum = 0;
float alpha = 100;
int currentEpoch = 0;
int hideMode = 0;
float stopgo = 1.0;
float DIRECTION = pow(-1.0,int(random(0,100)));
float fadeLength = 3;
boolean running = false;
float setSpeed = 30;
float speed = 30;

boolean single_run = false;
//Drawing variables
int sqBar; 
int _height = 1280; ///also set size in setup because stupid bug
String myIP;
int IPVal;
int [] IPinfo;
boolean ANDROID = true;

Dots group1 = new Dots(100,0,1,int(_height*0.75), int(_height*0.25), false); // nDots, speed, direction, opacity, randomMotion
Dots group2 = new Dots(100,0,-1,int(_height*0.25), int(_height*0.5), false); // nDots, speed, direction, opacity, randomMotion
Dots group3 = new Dots(100,0,1,int(_height*0.75), int(_height*0.75), false); // nDots, speed, direction, opacity, randomMotion


void setup(){
  myIP = KetaiNet.getIP();
  IPinfo = int(split(myIP, "."));
  IPVal = IPinfo[3] - 100;
  
  println("IP ADDRESS IS: ", myIP, ". IPVAL IS: ", str(IPVal));
  
  //randomSeed(10);
  //colorMode(HSB, 100,100,100,100);
  size(1280, 1280, P3D);//fullScreen();
  data = createGraphics(_height, _height);
  spout = new Spout(this);
  spout.createSender("dotbot Processing");
  ellipseMode(CENTER);
  sqBar = 0;//(width - height) /2;
  
  cP5 = new ControlP5(this);
  
  cP5.addSlider("nDotsSlider")
     .setPosition(sqBar-250,90)
     .setSize(200,28)
     .setRange(0,2000)
     .setNumberOfTickMarks(201)
     .setValue(500)
     ;
  cP5.addSlider("dotSize")
     .setPosition(sqBar-250,50)
     .setSize(200,28)
     .setRange(0,200)
     .setNumberOfTickMarks(201)
     .setValue(50)
     ;  
     
  cP5.addSlider("setSpeed")
     .setPosition(sqBar-250,130)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(21)
     .setValue(35)
     ;  
  cP5.addBang("Go",sqBar-180,180,60,30);

  if (IPVal == 12){ dotSize = 20;
                    nDotsSlider = 1000;    }
                    



  group1.Init();
  nDots = nDotsSlider;
  group1.Set(int(nDots), 0, pow(-1, int(random(0,100))));
  String message = ("IP\tTimestamp\tnDots\tdotSize\tspeed\tdir\tcoh\tcomment\n");
  logEntry(message, true);
  Go();

}

void keyPressed(){
  if (key == CODED) {
    if (keyCode == UP) {
      Go();
    } 
    else if (keyCode == DOWN) {
      Go();;
    }
  }
  
}






void Go(){
  goNoGo = true;
  t0 = millis()-1000000;
  nDots = nDotsSlider;
  //group1.Set(int(nDots*(C)), 0, 1);
  //group2.Set(int(nDots*(1-C)), 0, 1);
  //group1.Init();
  //group2.Init();
  //group1.Set(nDots, speed, 1); 
}



void logEntry(String msg, boolean append) { 
  //if (IPVal == 12){
  //  File file = new File("
  
  try {
    File file =new File("Z:/Dan_storage/dotbot_temp_logs/dotbot_log_temp.txt");
    if (!file.exists()) {
      file.createNewFile();
    }
 
    FileWriter fw = new FileWriter(file, append);///true = append
    BufferedWriter bw = new BufferedWriter(fw);
    PrintWriter pw = new PrintWriter(bw);

    pw.write(msg);
    pw.close();
  }
  catch(IOException ioe) {
    System.out.println("Exception ");
    ioe.printStackTrace();
  }
}

public String RTFN(){
  Calendar cal = Calendar.getInstance(TimeZone.getTimeZone("GMT"));
  String foo;
  foo = formatter.format(cal.getTimeInMillis());
  return foo;
}


void squareFrame(){
  data.fill(0,0,0,255);
  data.rect(0,0,sqBar, _height);
  data.rect(_height - sqBar,0,sqBar, _height);
}

void hideFrame(float alpha){
  data.fill(255,255,255,2.55*alpha);
  data.rect(0,0,_height, _height);
}


public class Dots {
  int NUMBER_OF_THINGS;
  float vel;  // speed and direction of rotation
  float dir;  // make 1 to move (positive for clockwise)
  int CENTREX;
  int CENTREY;
  float fade;
  int myFrameCount;
  boolean RAND;
  Dot[] DotList;
  
  public Dots(int numDots, float _vel,  float _dir, int centrex, int centrey, boolean _RAND) { 
    
    NUMBER_OF_THINGS = numDots; 
    vel =  _vel / 1000.0;
    dir = _dir;
    CENTREX = centrex;
    CENTREY = centrey;
    RAND = _RAND;
    Init();
  }      
  
  public void Reset(){
    Init();
  }
  
  private void Init() {
    
    //ArrayList<Dot> DotList = new ArrayList<Dot>(NUMBER_OF_THINGS);
    DotList = new Dot[nDots];
    for (int i=0; i< nDots; i++){
      DotList[i] = (new Dot(random(0, TWO_PI), this.vel, this.dir, this.CENTREX, this.CENTREY));//Dot(float rotation, float vel, float dir, int centreX, int centreY)
    }
  }
  void update() { 
    for(int i=0; i < this.NUMBER_OF_THINGS; i++){           //DotList.length; i++){  //for (Dot dot : DotList){
      Dot dot = DotList[i];
      if (RAND == true){ dot.randomMotion();}
      else {dot.renew(); }
      data.fill(0,0,0,255);
      data.ellipse(dot.X1, dot.Y1, dot.SIZE, dot.SIZE);
    }
  }
  void Resize(float lowBound, float highBound) { 
    for(int i=0; i < nDots; i++){  //for (Dot dot : DotList){
      DotList[i].Resize(random(lowBound, highBound));
    }
  }
  void Set(int _numDots, float _Vel, float _Dir) {
    NUMBER_OF_THINGS = _numDots;
    vel = _Vel / 1000.0;
    dir = _Dir; 
    for(int i=0; i < _numDots; i++){  //for (Dot dot : DotList){
      DotList[i].setVEL = vel*dir;
      DotList[i].DIR = dir;
    }
    String message = (myIP + '\t' + RTFN() + '\t' + str(_numDots) + '\t' + str(dotSize) + '\t' + str(vel) +'\t' + str(dir) + '\t' + str(1) + '\t' + "Set Values"+'\n');
    
    println(message);
    logEntry(message, true);
    //_Dots.changeArrayLength(_numDots);
    //_Dots.Reset();
  }

}
  
class Dot{
  float X1, Y1, ROTATION, RAD, SIZE;
  float COLOUR, setVEL, VEL, DIR, CX, CY, VAR, XDIR, YDIR;
  
  Dot(float rotation, float vel, float dir, int centreX, int centreY) {
    this.SIZE = random(dotSize,dotSize);
    this.COLOUR = random(100,100);  
    this.CX = centreX;
    this.CY = centreY;
    this.RAD = random(0, _height/4); //LAZY
    this.ROTATION = rotation;
    this.setVEL = vel*random(0.2,1.5);
    this.VEL = setVEL;
    this.DIR = dir;
    this.X1 = random(0,1.42)*_height + sqBar; 
    this.Y1 = random(0,1.42)*_height;
    this.VAR = random(0.1, 0.4);
    this.XDIR = random(-1,1);  // component vector
    this.YDIR = sqrt(1 - this.XDIR) * pow(-1.0, int(random(0,100)));   // randomly positive or negative component vector
    //this.RAD = sqrt(sq((this.X1 - _height/2)) + sq((this.Y1-_height/2)));
  }
  
  void randomMotion() {
    if (this.setVEL == 0){ this.VEL=0;}
    else {
    this.VEL = this.VEL + (this.setVEL - this.VEL)/(fadeLength*100);
    }
    this.RAD = sqrt(sq((this.X1 - _height/2)) + sq((this.Y1-_height/2)));
    this.X1 = this.X1 + this.XDIR*this.VEL*this.RAD + random(-0.5,0.5);
    this.Y1 = this.Y1 + this.YDIR*this.VEL*this.RAD + random(-0.5,0.5);
    
    if (this.X1 > (_height + this.SIZE + sqBar)) { this.X1 = (0 - this.SIZE + sqBar);}
    else if (this.X1 < (sqBar-this.SIZE)) { this.X1 = (_height + this.SIZE + sqBar);}
    if (this.Y1 > _height + this.SIZE) { this.Y1 = (0 - this.SIZE);}
    else if (this.Y1 < (0-this.SIZE)) { this.Y1 = (_height + this.SIZE);}
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
  data.beginDraw();
  data.background(255);
  data.fill(0);
  if (finished == true){
    println("Protocol complete");    
    String message = (myIP + '\t' + RTFN() + "\t--\t--\t--\t--\t--\tProtocol completed"+'\n');
    logEntry(message, true);
    noLoop();}
  else if (goNoGo == true){
      
    tLoop = millis();
    if (loopnum >= 6){ finished = true;
                                            hideMode=1;
                                            running = false;
    }
    
  
    
    if (running == false){ hideMode = 1;}
    
    // start actions at pre-determined times, but stagger them to avoid simulateously starting experiments
    if (running==false){//((second() == 40) && (running == false)){
      if (true){//((minute() == IPVal) ||  (minute() == IPVal+20) || (minute() == IPVal+40)){
        hideMode = 0;
        running = true;    
        String message = ("IP\tTimestamp\tnDots\tdotSize\tspeed\tdir\tcoh\tcomment\n");
        logEntry(message, false);
      }
    }
    // stop actions at pre-determined times, setup for next round, then wait
    if ((running == true) && (currentEpoch >= 6)){// ( (minute() == IPVal + 11) ||  (minute() == IPVal+31) || (minute() == IPVal-9))){
      group1.Set(0, 0, 0);
      hideMode = 1;
      running = false;
      currentEpoch = 0;
      loopnum += 1;
      
    }        
    // change experiment conditions every 90 seconds                             ***********************STIM DURATION DEFINED HERE*****************
    if ((running == true) && ( tLoop - t0 >= 60000)){
        //randomly choose direction every 60s. this will randomize time between reversals
        group1.Set(int(nDots), speed, pow(-1, int(random(0,100))));
        currentEpoch  = currentEpoch +1;
        t0 = tLoop;
    }
  

  }
  background(255);
  group1.update();
  hideFrame(alpha*hideMode);
  squareFrame();
  data.endDraw();
  spout.sendTexture(data);
}
void stop() {
  println(RTFN() + "\t VCRDR_log stopped \n");
  logEntry(RTFN() + "\t VCRDR_log stopped.\n", true);
}
