
import java.io.FileWriter;
import java.io.*;
import java.util.*;
import java.math.BigDecimal;
import java.text.DecimalFormat;
import java.time.Instant;
import java.sql.Timestamp;
import java.util.Collections;
import java.net.*;
import ketai.net.KetaiNet;
//import spout.*;
//Spout spout;

// PImage keeps alpha channel intact, unlike other drawing methods in Processing
//PGraphics data;



boolean goNoGo = false;
boolean finished = false;

//Logging setup
FileWriter fw;
BufferedWriter bw;
DecimalFormat formatter = new DecimalFormat("###.#");



int dotSize = 20;  // size of dots

int nDots = 100;  //number of dots
int cogRadius = 422;
int rotationRadius = 338;
float setSpeed = 20;
float speed = 20;

Dots group1 = new Dots(nDots,speed,1,100, false); // nDots, speed, direction, opacity, randomMotion
Dots group2 = new Dots(nDots,speed,-1,100, false); // nDots, speed, direction, opacity, randomMotion
Dots group3 = new Dots(nDots,speed,1,100, false); // nDots, speed, direction, opacity, randomMotion

int t0;
int tLoop;
int loopnum = 0;
float alpha = 100;
int currentEpoch = 0;
int hideMode = 1;
float stopgo = 1.0;
float DIRECTION = pow(-1.0,int(random(0,100)));
float fadeLength = 3;
boolean running = false;

boolean single_run = false;
//Drawing variables
int sqBar; 
int _height = 1280; ///also set size in setup because stupid bug
String myIP;
int IPVal;
int [] IPinfo;
boolean ANDROID = true;

void setup(){
  try
  {
    // To work, this needs connectivity to the specified server
    Socket socket = new Socket();
    socket.connect(new InetSocketAddress("google.com", 80));
    InetAddress addr = socket.getLocalAddress();
    myIP = addr.getHostAddress();
    socket.close();
  }
  catch( Exception e )
  {
    myIP = "0.0.0.0";
    println( e.getMessage() );
  }  
  IPinfo = int(split(myIP, "."));
  IPVal = IPinfo[3] - 100;
  
  println("IP ADDRESS IS: ", myIP, ". IPVAL IS: ", str(IPVal));
  
  //randomSeed(10);
  //colorMode(HSB, 100,100,100,100);
  fullScreen();
  println(width, height);
  //data = createGraphics(height, height);
  //spout = new Spout(this);
  //spout.createSender("dotbot Processing");
  ellipseMode(CENTER);
  sqBar = (width - height) /2;

                    



  group1.Init(0);
  group2.Init(TWO_PI/3.0);
  group3.Init(2*TWO_PI/3.0);
  
  //group1.Set(int(nDots), 0, pow(-1, int(random(0,100))));
  //String message = ("IP\tTimestamp\tnDots\tdotSize\tspeed\tdir\tCX\tCY\tcomment\n");
  //logEntry(message, true);
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
  else if (key =='s'){
    startStim();
  }
  
  
}


void startStim(){
    if (hideMode == 1){
      hideMode = 0;
      running = true;    
      String message = ("IP\tTimestamp\tnDots\tdotSize\tspeed\tdir\tCX\tCY\tcomment\n");
      logEntry(message, false);
    }
    else if (hideMode == 0){
        hideMode = 1;
        running = false;
        String message = (myIP + '\t' + RTFN() + '\t' + "Stim stopped");
        logEntry(message, true);
    }
}



void Go(){
  goNoGo = true;
  t0 = millis()-1000000;
  //group1.Set(int(nDots*(C)), 0, 1);
  //group2.Set(int(nDots*(1-C)), 0, 1);
  //group1.Init();
  //group2.Init();
  //group1.Set(nDots, speed, 1); 
}



void logEntry(String msg, boolean append) { 
  String filename;
  if (IPVal == 12){ filename = "Z:/Dan_storage/dotbot_temp_logs/dotbot_log_temp.txt";}
  else { filename = "/sdcard/dotbot/dotbot_log.txt";}
  
  try {
    File file =new File(filename);
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
  fill(0,0,0,255);
  rect(0,0,sqBar, height);
  rect(width - sqBar,0,sqBar, height);
}

void hideFrame(float alpha){
  fill(255,255,255,2.55*alpha);
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
  float CX;
  float CY;
  float ROTATION;
  float rotationVelocity = 0;//0.001;
  Dot[] DotList;
  
  public Dots(int numDots, float _vel,  float _dir, int colour, boolean _RAND) { 
    
    NUMBER_OF_THINGS = numDots; 
    this.vel =  _vel / 1000.0;
    this.dir = _dir;
    COLOUR = colour;
    RAND = _RAND;
  }      

  
  private void Init(float ROTATION) {
    this.ROTATION = ROTATION;
    this.CX = (width/2) + cos(ROTATION)*rotationRadius;
    this.CY = (height/2) + sin(ROTATION)*rotationRadius;
    
    //ArrayList<Dot> DotList = new ArrayList<Dot>(NUMBER_OF_THINGS);
    DotList = new Dot[nDots];
    for (int i=0; i< nDots; i++){
      DotList[i] = (new Dot(random(0, TWO_PI), this.vel, this.dir, this.CX, this.CY));
    }
    Set(NUMBER_OF_THINGS, speed, this.dir);
  }
  void update() { 
    
    this.ROTATION = this.ROTATION + this.rotationVelocity;
    this.CX = (cos(this.ROTATION)*rotationRadius) + width/2 ;
    this.CY = (sin(this.ROTATION)*rotationRadius) + height/2  ;
    for(int i=0; i < this.NUMBER_OF_THINGS; i++){           //DotList.length; i++){  //for (Dot dot : DotList){
      Dot dot = DotList[i];
      if (RAND == true){ dot.randomMotion();}
      else {dot.reCentre(this.CX, this.CY);  // 
            dot.renew(); }
      fill(0,0,0,2.55*this.COLOUR);
      ellipse(dot.X1, dot.Y1, dot.SIZE, dot.SIZE);
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
    String message = (myIP + '\t' + RTFN() + '\t' + str(_numDots) + '\t' + str(dotSize) + '\t' + str(vel) +'\t' + str(dir) + '\t' + str(this.CX) + '\t' +str(this.CY) + '\t' + "Set Values"+'\n');
    
    println(message);
    logEntry(message, true);
    //_Dots.changeArrayLength(_numDots);
    //_Dots.Reset();
  }

}
  
class Dot{
  float X1, Y1, ROTATION, RAD, SIZE;
  float COLOUR, setVEL, VEL, DIR, CX, CY, VAR, XDIR, YDIR;
  
  Dot(float rotation, float vel, float dir, float _cx, float _cy) {
    this.SIZE = random(dotSize,dotSize);
    this.COLOUR = random(100,100);  
    this.CX = _cx;
    this.CY = _cy;
    this.ROTATION = rotation;
    this.setVEL = vel*random(0.7,1.3);
    this.VEL = setVEL*dir;
    this.DIR = dir;
    this.X1 = random(-1*cogRadius, cogRadius) + this.CX; 
    this.Y1 = random(-1*cogRadius, cogRadius) + this.CY;
    this.VAR = random(0.1, 0.4);
    this.XDIR = random(-1,1);  // component vector
    this.YDIR = sqrt(1 - this.XDIR) * pow(-1.0, int(random(0,100)));   // randomly positive or negative component vector
    this.RAD = sqrt(sq((this.X1 - this.CX)) + sq((this.Y1-this.CY)));
  }
  
  void randomMotion() {
    if (this.setVEL == 0){ this.VEL=0;}
    else {
    this.VEL = this.VEL + (this.setVEL - this.VEL)/(fadeLength*100);
    }
    this.RAD = sqrt(sq((this.X1 - width/2)) + sq((this.Y1-height/2)));
    this.X1 = this.X1 + this.XDIR*this.VEL*this.RAD + random(-0.5,0.5);
    this.Y1 = this.Y1 + this.YDIR*this.VEL*this.RAD + random(-0.5,0.5);
    
    if (this.X1 > (width + this.SIZE + sqBar)) { this.X1 = (0 - this.SIZE + sqBar);}
    else if (this.X1 < (sqBar-this.SIZE)) { this.X1 = (width + this.SIZE + sqBar);}
    if (this.Y1 > height + this.SIZE) { this.Y1 = (0 - this.SIZE);}
    else if (this.Y1 < (0-this.SIZE)) { this.Y1 = (height + this.SIZE);}
  }
  
  void renew() {
    
    if (this.setVEL == 0){ this.VEL=0;}
    else {
    this.VEL = this.VEL + (this.setVEL - this.VEL)/(fadeLength*100);
    }
    if (random(0,1) > 0.9){
        this.X1 = random(-1*cogRadius, cogRadius) + this.CX; 
        this.Y1 = random(-1*cogRadius, cogRadius) + this.CY;
    }
    this.ROTATION = this.ROTATION + this.VEL;
    this.X1 = (cos(this.ROTATION)*this.RAD + cos(this.VAR*this.ROTATION)) + this.CX ;
    this.Y1 = (sin(this.ROTATION)*this.RAD + sin(this.VAR*this.ROTATION)) + this.CY ;
  }
  void reCentre(float cx, float cy){
    
    this.CX = cx;
    this.CY = cy;
  }
}


void draw(){
  //data.beginDraw();
  background(255,255,255,255);
  fill(0,0,0,255);
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
    if ((second() == 40) && (running == false)){
      if ((minute() == IPVal) ||  (minute() == IPVal+20) || (minute() == IPVal+40)){
        startStim();
      }
    }
    // stop actions at pre-determined times, setup for next round, then wait
    if ((running == true) && (currentEpoch >= 18)){// ( (minute() == IPVal + 11) ||  (minute() == IPVal+31) || (minute() == IPVal-9))){
      //group1.Set(0, 0, 0);
      hideMode = 1;
      running = false;
      currentEpoch = 0;
      loopnum += 1;
      
    }        
    // report centres every 10 seconds                             ***********************STIM DURATION DEFINED HERE*****************
    if ((running == true) && ( tLoop - t0 >= 10000)){
        String message = (myIP + '\t' + RTFN() + '\t' + str(group1.NUMBER_OF_THINGS) + '\t' + str(dotSize) + '\t' + str(group1.vel) +'\t' + str(group1.dir) + '\t' + str(group1.CX) + '\t' +str(group1.CY) + '\t' + "group1"+'\n');
        println(message);
        logEntry(message, true);   
        String message2 = (myIP + '\t' + RTFN() + '\t' + str(group2.NUMBER_OF_THINGS) + '\t' + str(dotSize) + '\t' + str(group2.vel) +'\t' + str(group2.dir) + '\t' + str(group2.CX) + '\t' +str(group2.CY) + '\t' + "group2"+'\n');
        println(message2);
        logEntry(message2, true);    
        String message3 = (myIP + '\t' + RTFN() + '\t' + str(group3.NUMBER_OF_THINGS) + '\t' + str(dotSize) + '\t' + str(group3.vel) +'\t' + str(group3.dir) + '\t' + str(group3.CX) + '\t' +str(group3.CY) + '\t' + "group3"+'\n');
        println(message3);
        logEntry(message3, true);         
        currentEpoch  = currentEpoch +1;
        t0 = tLoop;
    }
  

  }
  background(255,255,255,255);
  group1.update();
  group2.update();
  group3.update();
  hideFrame(alpha*hideMode);
  squareFrame();
  //data.endDraw();
  //spout.sendTexture(data);
}
void stop() {
  println(RTFN() + "\t VCRDR_log stopped \n");
  logEntry(RTFN() + "\t VCRDR_log stopped.\n", true);
}
