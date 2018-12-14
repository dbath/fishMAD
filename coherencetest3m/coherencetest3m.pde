
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

int nDots = 2000;  //number of dots
int nDotsSlider;

Dots group1 = new Dots(2000,0,1,100, false); // nDots, speed, direction, opacity, randomMotion
Dots group2 = new Dots(2000,0,1,100, true); // nDots, speed, direction, opacity, randomMotion

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
FloatList coherences;
float C;

boolean single_run = false;
//Drawing variables
int sqBar; 
int _height = 1280; ///also set size in setup because stupid bug
String myIP;
int IPVal;
int [] IPinfo;
boolean ANDROID = true;

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
                    


  coherences = new FloatList();
  coherences.append(0.00);
  coherences.append(0.00);
  coherences.append(0.20);
  coherences.append(0.20);
  coherences.append(0.40);
  coherences.append(0.40);
  coherences.append(0.60);
  coherences.append(0.20);
  coherences.append(0.80);
  coherences.append(0.40);
  coherences.append(1.00);
  coherences.append(0.00);
  println(coherences.size());
  coherences.shuffle();
  println(coherences);
  C = coherences.get(loopnum);
  println(str(C));
  group1.Init();
  group2.Init();
  nDots = nDotsSlider;
  group1.Set(int(nDots*(C)), 0, 1);
  group2.Set(int(nDots*(1-C)), 0, 1);
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
      DotList[i] = (new Dot(random(0, TWO_PI), this.vel, this.dir));
    }
  }
  void update() { 
    for(int i=0; i < this.NUMBER_OF_THINGS; i++){           //DotList.length; i++){  //for (Dot dot : DotList){
      Dot dot = DotList[i];
      if (RAND == true){ dot.randomMotion();}
      else {dot.renew(); }
      data.fill(0,0,0,2.55*this.COLOUR);
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
    String message = (myIP + '\t' + RTFN() + '\t' + str(_numDots) + '\t' + str(dotSize) + '\t' + str(vel) +'\t' + str(dir) + '\t' + str(C) + '\t' + "Set Values"+'\n');
    logEntry(message, true);
    //_Dots.changeArrayLength(_numDots);
    //_Dots.Reset();
  }

}
  
class Dot{
  float X1, Y1, ROTATION, RAD, SIZE;
  float COLOUR, setVEL, VEL, DIR, CX, CY, VAR, XDIR, YDIR;
  
  Dot(float rotation, float vel, float dir) {
    this.SIZE = random(dotSize,dotSize);
    this.COLOUR = random(100,100);  
    this.CX = _height/2;
    this.CY = _height/2;
    this.ROTATION = rotation;
    this.setVEL = vel*random(0.7,1.3);
    this.VEL = setVEL;
    this.DIR = dir;
    this.X1 = random(0,1.42)*_height + sqBar; 
    this.Y1 = random(0,1.42)*_height;
    this.VAR = random(0.1, 0.4);
    this.XDIR = random(-1,1);  // component vector
    this.YDIR = sqrt(1 - this.XDIR) * pow(-1.0, int(random(0,100)));   // randomly positive or negative component vector
    this.RAD = sqrt(sq((this.X1 - _height/2)) + sq((this.Y1-_height/2)));
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
    if (loopnum >= coherences.size()){ finished = true;
                                            hideMode=1;
                                            running = false;
    }
    
  
    
    if (running == false){ hideMode = 1;}
    
    // start actions at pre-determined times, but stagger them to avoid simulateously starting experiments
    if ((second() == 40) && (running == false)){
      if ((minute() == IPVal) ||  (minute() == IPVal+20) || (minute() == IPVal+40)){
        hideMode = 0;
        running = true;    
        String message = ("IP\tTimestamp\tnDots\tdotSize\tspeed\tdir\tcoh\tcomment\n");
        logEntry(message, false);
      }
    }
    // stop actions at pre-determined times, setup for next round, then wait
    if ((running == true) && (currentEpoch >= 2)){// ( (minute() == IPVal + 11) ||  (minute() == IPVal+31) || (minute() == IPVal-9))){
      group1.Set(0, 0, 0);
      group2.Set(0, 0, 0);
      hideMode = 1;
      running = false;
      currentEpoch = 0;
      loopnum += 1;
      C = coherences.get(loopnum);
      DIRECTION = pow(-1, int(random(0,100))); // random 1 or -1
      println(str(C), " ", str(DIRECTION));
      
    }        
    // change experiment conditions every 300 seconds                             ***********************STIM DURATION DEFINED HERE*****************
    if ((running == true) && ( tLoop - t0 >= 300000)){
        
        if (currentEpoch == 0 ){      group1.Set(int(nDots*(C)), speed, DIRECTION);
                                      group2.Set(int(nDots*(1-C)), speed, -1*DIRECTION);}
        else if (currentEpoch == 1 ){ group1.Set(int(nDots*(C)), 0, 1);
                                      group2.Set(int(nDots*(1-C)), 0, 1);  
                                      hideMode=1;}
        /*
        else if (currentEpoch == 3 ){ group1.Set(int(nDots*(C)), 0, 0);
                                      group2.Set(int(nDots*(1-C)), 0, 0);}
        else if (currentEpoch == 5 ){ group1.Set(int(nDots*(C)), 0, 1);
                                      group2.Set(int(nDots*(1-C)), 0, 1);}
        else if (currentEpoch == 6 ){ group1.Set(int(nDots*(C)), speed, -1);
                                      group2.Set(int(nDots*(1-C)), speed, -1); }
        else if (currentEpoch == 7 ){ group1.Set(int(nDots*(C)), speed, 1);
                                      group2.Set(int(nDots*(1-C)), speed, 1); }
        else if (currentEpoch == 8 ){ group1.Set(int(nDots*(C)), speed, 1);
                                      group2.Set(int(nDots*(1-C)), speed, -1); }
        */
        currentEpoch  = currentEpoch +1;
        t0 = tLoop;
    }
  

  }
  background(255);
  group1.update();
  group2.update();
  hideFrame(alpha*hideMode);
  squareFrame();
  data.endDraw();
  spout.sendTexture(data);
}
void stop() {
  println(RTFN() + "\t VCRDR_log stopped \n");
  logEntry(RTFN() + "\t VCRDR_log stopped.\n", true);
}
