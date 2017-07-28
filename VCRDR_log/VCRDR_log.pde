import java.io.FileWriter;
import java.io.*;
import java.util.*;
import java.math.BigDecimal;
import java.text.DecimalFormat;
import java.time.Instant;
import java.sql.Timestamp;
import java.util.Collections;


//Logging setup
FileWriter fw;
BufferedWriter bw;
DecimalFormat formatter = new DecimalFormat("###.#");


//Scheduling
int[] transitions = { 0,20,200,400,600,800,1000,1200,1400,1600, 1800 };
int[] speeds = {15, 45, 30};
int loopnum = 0;
int tEnd = 1800;
int currentEpoch = 0; 
int t0;
int tLoop;
float alpha = 100;
int fadeTime = 1;
boolean running;
int speed = 15;
int nDots = 500;
float C = 1.0;   //coherence
boolean single_run = false;
//Drawing variables
int sqBar; 

Dots group1 = new Dots(nDots,0,1,1);
//Dots group2 = new Dots(round(nDots*(1-C)),0,1,1);

void setup(){
  
  randomSeed(10);
  colorMode(HSB, 100,100,100,100);
  fullScreen();
  ellipseMode(CENTER);
  sqBar = (width - height) /2;
  stroke(0,0,0,0);
  fill(55,100,100,100);; 
  running = true;
  t0 = millis();
  group1.Init();
  logEntry(RTFN() + '\t' + str(nDots) + '\t' + str(C) + '\t' + str(group1.vel) +'\t' + str(group1.dir) + '\n');
  println(RTFN() + "\t Protocol initiated with " + str(nDots) + " dots spinning at " + str(speed) + ".\n");
}




void logEntry(String msg) { 
  try {
    File file =new File("/sdcard/dan_Data/dotbot_log.txt");
    if (!file.exists()) {
      file.createNewFile();
    }
 
    FileWriter fw = new FileWriter(file, true);///true = append
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
  fill(55,100,85,alpha);
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
    DotList = new Dot[NUMBER_OF_THINGS];
    for (int i=0; i< DotList.length; i++){
      DotList[i] = (new Dot(random(0, TWO_PI), vel, dir));
    }
  }
  void update() { 
    for(int i=0; i < DotList.length; i++){  //for (Dot dot : DotList){
      Dot dot = DotList[i];
      dot.renew();
      fill(0,100,00,dot.COLOUR);
      ellipse(dot.X1, dot.Y1, dot.SIZE, dot.SIZE);
    }
  }
  void Resize(float lowBound, float highBound) { 
    for(int i=0; i < DotList.length; i++){  //for (Dot dot : DotList){
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
    this.SIZE = random(40,50);
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
    this.ROTATION = this.ROTATION + this.VEL*this.DIR*(1.0-(alpha/100.0));
    this.X1 = (cos(this.ROTATION)*this.RAD + sin(this.VAR*this.ROTATION)) + this.CX ;
    this.Y1 = (sin(this.ROTATION)*this.RAD + sin(this.VAR*this.ROTATION)) + this.CY ;
  }
  void Resize(float sizeFactor){
    this.SIZE = this.SIZE*sizeFactor;
  }
}


void draw(){
  
  tLoop = millis();
  
  if ((tLoop - t0 >= tEnd*1000 ) && (running == true)) {  
    if (single_run){
      logEntry(RTFN() + "\t protocol complete. \n");
      println("PROTOCOL COMPLETE");
      running = false;
      alpha = 100; 
    }
    else {
      logEntry(RTFN() + "\t " + str(speeds[loopnum]) + " protocol complete. \n");
      println(RTFN() + "\t " + str(speeds[loopnum]) + " protocol complete. \n");
      running = false; 
      alpha = 100;
    }  
  }
  
  if (tLoop - t0 >= tEnd*2000 ) {
    loopnum =  loopnum + 1;
    t0 = millis();
    tLoop = millis();
    currentEpoch = 0;
    speed = speeds[loopnum];
    running = true;
  }
  
  int timeLeft = transitions[currentEpoch +1]*1000 - (tLoop - t0);
  /*
  if (timeLeft <= fadeTime) {
    alpha = (float)((fadeTime - timeLeft)/(fadeTime/100.0));
  }
  else if ((tLoop - t0) <= fadeTime){
    alpha = (float)((fadeTime - (tLoop - t0))/(fadeTime/100.0));
  }
  else {
    alpha = 0.0;
  }
  */
  
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
    logEntry(RTFN() + '\t' + str(nDots) + '\t' + str(C) + '\t' + str(group1.vel) +'\t' + str(group1.dir) + '\n');
    println(message);
                    
    currentEpoch  = currentEpoch +1;
  }
    
  
  
  background(55,100,100,100);
  group1.update();
  
  hideFrame(alpha);
  squareFrame();
}
void stop() {
  println(RTFN() + "\t VCRDR_log stopped \n");
  logEntry(RTFN() + "\t VCRDR_log stopped.\n");
}