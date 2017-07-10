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
float alpha = 0.5;

//Drawing variables
int sqBar; 

Dots group1 = new Dots(300,3,1,1);

void setup(){
  
  randomSeed(10);
  colorMode(HSB, 100,100,100,100);
  fullScreen();
  ellipseMode(CENTER);
  sqBar = (width - height) /2;
  stroke(0,0,0,0);
  fill(55,100,100,100);; 
  group1.Init();
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
  String foo;
  foo = formatter.format(System.currentTimeMillis());
  return foo;
}


void squareFrame(){
  fill(0,0,0,100);
  rect(0,0,sqBar, height);
  rect(width - sqBar,0,sqBar, height);
}

void Set(Dots _Dots, int _numDots, float _Vel, float _Dir) {
  _Dots.NUMBER_OF_THINGS = _numDots;
  _Dots.vel = _Vel / 1000.0;
  _Dots.dir = _Dir;
  _Dots.changeArrayLength(_numDots);
  //_Dots.Reset();
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
  
  private void Init() {
    
    ArrayList<Dot> DotList = new ArrayList<Dot>();
    for (int i=0; i< NUMBER_OF_THINGS; i++){
      DotList.add(new Dot(random(0, TWO_PI), vel, dir));
    }
  }
  void update() { 
    for (Dot dot : DotList){
      dot.renew(dot.ROTATION + vel*dir*(1.0-(alpha/100.0)));
      fill(0,100,00,dot.COLOUR);
      ellipse(dot.X1, dot.Y1, dot.SIZE, dot.SIZE);
    }
  }
  void Resize(float lowBound, float highBound) { 
    for (Dot dot : DotList){
      dot.Resize(random(lowBound, highBound));
    }
  }
  void changeArrayLength(int newArrayLength) { 
    if (DotList.size() < newArrayLength) {
      for (int i=DotList.size(); i< newArrayLength; i++){
        Dot d = new Dot(random(0, TWO_PI), vel, dir);
        DotList.add(d);
      }
    } 
    if (DotList.size() > newArrayLength) {
      Collections.shuffle(DotList);
      for (int i=DotList.size(); i > newArrayLength; i--) {
        DotList.remove(i);
      }
    }
  }

  
class Dot{
  float X1, Y1, ROTATION, RAD, SIZE;
  float COLOUR,  VEL, DIR;
  
  Dot(float rotation, float vel, float dir) {
    this.SIZE = random(10,80);
    this.COLOUR = random(80,100);  
    this.ROTATION = rotation;
    this.VEL = vel;
    this.DIR = dir;
    this.X1 = random(0,1)*height + sqBar; 
    this.Y1 = random(0,1)*height;
    this.RAD = sqrt(sq((this.X1 - width/2)) + sq((this.Y1-height/2)));
  }
  
  void renew(float rotation) {
    this.X1 = (cos(rotation)*this.RAD) + width/2;
    this.Y1 = (sin(rotation)*this.RAD) + height/2;
    this.ROTATION = rotation;
  }
  void Resize(float sizeFactor){
    this.SIZE = this.SIZE*sizeFactor;
  }
}
}

void draw(){
  background(0,0,100,100);
  group1.update();
  
  //logEntry("hello world!\t" + RTFN() + '\n');
  print(RTFN());
  squareFrame();
}

 
 
 