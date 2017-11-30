
import java.io.FileWriter;
import java.io.*;
import java.util.*;
import java.math.BigDecimal;
import java.text.DecimalFormat;
import java.time.Instant;
import java.sql.Timestamp;
import java.util.Collections;


//GUI Setup

import controlP5.*;
ControlP5 cP5;
Slider abc;
boolean goNoGo = false;

//Logging setup
FileWriter fw;
BufferedWriter bw;
DecimalFormat formatter = new DecimalFormat("###.#");



int dotSize = 50;  // size of dots

int nDots = 500;  //number of dots
int nDotsSlider;

Dots group1 = new Dots(2000,0,1,1);

int t0;
int tLoop;
float alpha = 100;
int hideMode = 0;
float stopgo = 1.0;
int DIRECTION = 1;
int fadeTime = 1;
boolean running = false;
int speed = 35;
float C = 1.0;   //coherence
boolean single_run = false;
//Drawing variables
int sqBar; 

int bkgColour;
int dotColour;
int bkgBrightness;
int dotBrightness;


void setup(){

  
  
  randomSeed(10);
  colorMode(HSB, 100,100,100,100);
  fullScreen();
  ellipseMode(CENTER);
  sqBar = (width - height) /2;
  
  cP5 = new ControlP5(this);
  
  cP5.addSlider("bkgColour")
     .setPosition(sqBar-300,50)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(50)
     ;
    cP5.addSlider("dotColour")
     .setPosition(sqBar-300,90)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(50)
     ;  
    cP5.addSlider("bkgBrightness")
     .setPosition(sqBar-300,130)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(50)
     ;
    cP5.addSlider("dotBrightness")
     .setPosition(sqBar-300,170)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(50)
     ;  
    cP5.addSlider("speed")
     .setPosition(sqBar-300,210)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(21)
     .setValue(35)
     ;  
  cP5.addBang("Go",sqBar-220,250,60,30);
  cP5.addBang("Hide",sqBar-220,300,60,30);
  cP5.addBang("Reverse",sqBar-220,350,60,30);
  cP5.addBang("StopStart",sqBar-220,400,60,30);
   
  stroke(0,0,0,0);
  fill(55,80,100,100);; 

  group1.Init();

}

void keyPressed(){
  if (key == CODED) {
    if (keyCode == RIGHT) {
      bkgColour = bkgColour +2;
    } 
    else if (keyCode == LEFT) {
      bkgColour = bkgColour -2;
    }
    else if (keyCode == UP) {
      bkgBrightness = bkgBrightness +2;
    }
    else if (keyCode == DOWN) {
      bkgBrightness = bkgBrightness -2;
    }
  }
    
  if (key == 'r'){Reverse();}
  else if (key == 's'){StopStart();}
  else if (key == 'g'){Go();}
  else if (key == 'h'){Hide();}
  else if (key == 'k') {
    dotColour = dotColour +2;
  } 
  else if (key == 'j') {
    dotColour = dotColour -2;
  }
  else if (key == 'i') {
    dotBrightness = dotBrightness +2;
  }
  else if (key == 'm') {
    dotBrightness = dotBrightness -2;
  }
  
}


void Reverse(){
  DIRECTION = DIRECTION * -1; 
}

void StopStart(){
  stopgo = stopgo - 1.0;
  stopgo = abs(stopgo);    

}



void Go(){
  goNoGo = true;
  t0 = millis();
  group1.Init();
  group1.Set(nDots, speed, 1); 
  running = true;
}

void Hide(){
  hideMode = hideMode - 1;
  hideMode = abs(hideMode); 
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
  fill(0,0,0,100);
  rect(0,0,sqBar, height);
  rect(width - sqBar,0,sqBar, height);
}

void hideFrame(float alpha){
  fill(bkgColour,100,bkgBrightness,alpha);
  rect(0,0,width, height);
}


public class Dots {
  int NUMBER_OF_THINGS;
  float vel;  // speed and direction of rotation
  float dir;  // make 1 to move (positive for clockwise)
  int COLOUR;
  float fade;
  int myFrameCount;
  Dot[] DotList;
  
  public Dots(int numDots, float _vel,  float _dir, int colour) { 
    
    NUMBER_OF_THINGS = numDots; 
    vel =  _vel / 1000.0;
    dir = _dir;
    COLOUR = colour;
    Init();
  }      
  
  public void Reset(){
    Init();
  }
  
  public void Init() {
    
    //ArrayList<Dot> DotList = new ArrayList<Dot>(NUMBER_OF_THINGS);
    DotList = new Dot[nDots];
    for (int i=0; i< nDots; i++){
      DotList[i] = (new Dot(random(0, TWO_PI), vel, dir));
    }
  }
  void update() { 
    for(int i=0; i < nDots; i++){//DotList.length; i++){  //for (Dot dot : DotList){
      Dot dot = DotList[i];
      dot.renew();
      stroke(dotColour,100,dotBrightness,dot.COLOUR);
      fill(dotColour,100,dotBrightness,dot.COLOUR);
      ellipse(dot.X1, dot.Y1, dot.SIZE, dot.SIZE);
    }
  }
  void Resize(float lowBound, float highBound) { 
    for(int i=0; i < nDots; i++){  //for (Dot dot : DotList){
      DotList[i].Resize(random(lowBound, highBound));
    }
  }
  void Set(int _numDots, float _Vel, float _Dir) {
    this.NUMBER_OF_THINGS = _numDots;
    this.vel = _Vel / 1000.0;
    this.dir = _Dir; 
    for(int i=0; i < DotList.length; i++){  //for (Dot dot : DotList){
      DotList[i].VEL = this.vel;
      DotList[i].DIR = this.dir;
    }
    //_Dots.changeArrayLength(_numDots);
    //_Dots.Reset();
  }
/*  
  void changeArrayLength(int newArrayLength) { 
    if (DotList.length() < newArrayLength) {
      for (int i=DotList.length; i< newArrayLength; i++){
        Dot d = new Dot(random(0, TWO_PI), vel, dir);
        DotList[i] = d;
      }
    } 
    if (DotList.length > newArrayLength) {
      //Collections.shuffle(DotList);
      for (int i=DotList.length; i > newArrayLength; i--) {
        DotList.remove(i);
      }
    }
  }
*/
}
  
class Dot{
  float X1, Y1, ROTATION, RAD, SIZE;
  float COLOUR,  VEL, DIR, CX, CY, VAR;
  
  Dot(float rotation, float vel, float dir) {
    this.SIZE = random(dotSize,dotSize);
    this.COLOUR = random(100,100);  
    this.CX = width/2;
    this.CY = height/2;
    this.ROTATION = rotation;
    this.VEL = vel*random(0.7,1.3);
    this.DIR = dir;
    this.X1 = random(0,1.42)*height + sqBar; 
    this.Y1 = random(0,1.42)*height;
    this.RAD = sqrt(sq((this.X1 - width/2)) + sq((this.Y1-height/2)));
    this.VAR = random(0.1, 0.4);
  }
  
  void renew() {
    this.ROTATION = this.ROTATION + this.VEL*this.DIR*stopgo*DIRECTION;
    this.X1 = (cos(this.ROTATION)*this.RAD + sin(this.VAR*this.ROTATION)) + this.CX ;
    this.Y1 = (sin(this.ROTATION)*this.RAD + sin(this.VAR*this.ROTATION)) + this.CY ;
  }
  void Resize(float sizeFactor){
    this.SIZE = this.SIZE*sizeFactor;
  }
}


void draw(){
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
    
    background(bkgColour,100,bkgBrightness,100);
    group1.update();
    
    hideFrame(alpha*hideMode);
  }
  squareFrame();
}
void stop() {
  println(RTFN() + "\t VCRDR_log stopped \n");
  logEntry(RTFN() + "\t VCRDR_log stopped.\n", true);
}