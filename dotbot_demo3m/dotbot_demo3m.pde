
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

//Logging setup
FileWriter fw;
BufferedWriter bw;
DecimalFormat formatter = new DecimalFormat("###.#");



int dotSize = 1;  // size of dots

int nDots = 1000;  //number of dots
int nDotsSlider;

Dots group1 = new Dots(1000,0,1,100, false); // nDots, speed, direction, opacity, randomMotion
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



void setup(){

  myIP = KetaiNet.getIP();
  IPinfo = int(split(myIP, "."));
  IPVal = IPinfo[3] - 100;
  size(1280, 1280, P3D);//fullScreen();
  data = createGraphics(_height, _height);
  spout = new Spout(this);
  spout.createSender("dotbot demo");
  ellipseMode(CENTER);
  sqBar = 0;//(width - height) /2;
  
  cP5 = new ControlP5(this);
  
  cP5.addSlider("nDotsSlider")
     .setPosition(sqBar-200,90)
     .setSize(200,28)
     .setRange(0,2000)
     .setNumberOfTickMarks(201)
     .setValue(1000)
     ;
    cP5.addSlider("dotSize")
     .setPosition(sqBar-200,50)
     .setSize(200,28)
     .setRange(0,200)
     .setNumberOfTickMarks(201)
     .setValue(20)
     ;  
    cP5.addSlider("speed")
     .setPosition(sqBar-200,130)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(21)
     .setValue(30)
     ;  
  cP5.addBang("Go",sqBar-120,180,60,30);
  cP5.addBang("Hide",sqBar-120,250,60,30);
  cP5.addBang("Reverse",sqBar-120,330,60,30);
  cP5.addBang("StopStart",sqBar-120,410,60,30);
   



  group1.Init();
  nDots = nDotsSlider;
  group1.Set(int(nDots), 0, pow(-1, int(random(0,100))));
  String message = ("IP\tTimestamp\tnDots\tdotSize\tspeed\tdir\tcoh\tcomment\n");
  //logEntry(message, true);
  Go();
}

void keyPressed(){
  /*
  if (key == CODED) {
    if (keyCode == UP) {
      brightVal = brightVal +2;
    } 
    else if (keyCode == DOWN) {
      brightVal = brightVal -2;
    }
  }
  */
  if (key == 'r'){Reverse();}
  else if (key == 's'){StopStart();}
  else if (key == 'g'){Go();}
  else if (key == 'h'){Hide();}
  
}


void Reverse(){
  DIRECTION = DIRECTION * -1; 
  group1.Set(int(nDots), speed, DIRECTION);
  String message = (RTFN() + '\t' + str(nDots) + '\t' + str(dotSize) + '\t' + str(speed) +'\t' + str(DIRECTION) + '\t' + "reversed"+'\n');
  //logEntry(message, true);
  println(message);
}

void StopStart(){
  stopgo = stopgo - 1.0;
  stopgo = abs(stopgo);    
  group1.Set(int(nDots), speed*stopgo, DIRECTION);
  String message;
  if (stopgo == 1.0){message = (RTFN() + '\t' + str(nDots) + '\t' + str(dotSize) + '\t' + str(0) +'\t' + str(DIRECTION) + '\t' + "stopped"+'\n');}
  else {message = (RTFN() + '\t' + str(nDots) + '\t' + str(dotSize) + '\t' + str(speed) +'\t' + str(DIRECTION) + '\t' + "moving"+'\n');}
  //logEntry(message, true);
  println(message);

}



void Go(){
  goNoGo = true;
  t0 = millis();
  nDots = nDotsSlider;
  group1.Init();
  group1.Set(nDots, speed, 1); 
  String message;
  if (hideMode == 1.0){message = (RTFN() + '\t' + str(nDots) + '\t' + str(dotSize) + '\t' + str(speed) +'\t' + str(DIRECTION) + '\t' + "Initiated (hidden)"+'\n');}
  else {message = (RTFN() + '\t' + str(nDots) + '\t' + str(dotSize) + '\t' + str(speed) +'\t' + str(DIRECTION) + '\t' + "Initiated"+'\n');}
  //logEntry(message, true);
  println(message);
  println(message);
  running = true;
}

void Hide(){
  hideMode = hideMode - 1;
  hideMode = abs(hideMode); 
  String message;
  if (hideMode == 1.0){ message = (RTFN() + '\t' + str(0) + '\t' + str(dotSize) + '\t' + str(speed) +'\t' + str(DIRECTION) + '\t' + "hidden"+'\n');}
  else { message = (RTFN() + '\t' + str(nDots) + '\t' + str(dotSize) + '\t' + str(speed) +'\t' + str(DIRECTION) + '\t' + "unhidden"+'\n');}
  //logEntry(message, true);
  println(message);
}



void logEntry(String msg, boolean append) { 
  try {
    File file =new File("/sdcard/dotbot/dotbot_log.txt");
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
  if (goNoGo == true){
    tLoop = millis();
    running = true;
    /*
    if ((tLoop - t0 >= tEnd*1000 ) && (running == true)) {  
      if (single_run){
        logEntry(RTFN() + "\t protocol complete. \n", true);
        println("PROTOCOL COMPLETE");
        running = false;
        alpha = 100; 
      }
      else {
        logEntry(RTFN() + "\t " + str(speeds[loopnum]) + " protocol complete. \n", true);
        println(RTFN() + "\t " + str(speeds[loopnum]) + " protocol complete. \n");
        running = false; 
        alpha = 100;
      }  
    }
    
    if (tLoop - t0 >= tEnd*1000 ) {
      loopnum =  loopnum + 1;
      t0 = millis();
      tLoop = millis();
      currentEpoch = 0;
      speed = speeds[loopnum];
      running = true;
    }
    
    int timeLeft = transitions[currentEpoch +1]*1000 - (tLoop - t0);
    
    if (timeLeft <= fadeTime) {
      alpha = (float)((fadeTime - timeLeft)/(fadeTime/100.0));
    }
    else if ((tLoop - t0) <= fadeTime){
      alpha = (float)((fadeTime - (tLoop - t0))/(fadeTime/100.0));
    }
    else {
      alpha = 0.0;
    }
    
    
    if (((tLoop - t0) > transitions[currentEpoch +1]*1000) && (running == true) ){
      if (currentEpoch == 0 ){ group1.Set(nDots, 0, 1);
                               alpha = 0.0;}
      else if (currentEpoch == 1 ){ group1.Set(nDots, 0, -1); }
      else if (currentEpoch == 2 ){ group1.Set(nDots, speed, -1); }
      else if (currentEpoch == 3 ){ group1.Set(nDots, speed, 1); }
      else if (currentEpoch == 4 ){ group1.Set(nDots, 0, 1); }
      else if (currentEpoch == 5 ){ group1.Set(nDots, speed, 1);  }
      else if (currentEpoch == 6 ){ group1.Set(nDots, speed, -1);  }
      else if (currentEpoch == 7 ){ group1.Set(nDots, 0, -1);  }
      String message = (RTFN() + "\t transition " + str(currentEpoch) + " initiated: V:" + str(group1.vel) + "\tD:" + str(group1.dir) + " \n");
      logEntry(RTFN() + '\t' + str(nDots) + '\t' + str(C) + '\t' + str(group1.vel) +'\t' + str(group1.dir) + '\n', true);
      println(message);
                      
      currentEpoch  = currentEpoch +1;
    }
      
    */
    
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
