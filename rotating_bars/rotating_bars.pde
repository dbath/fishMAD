

int t0;
int t1;
int startTime;
boolean tick = false;
int wait = 1*10*1000;
int counter = 0;
int alpha = 0;
int fadeTime = 3000;

Bars test1 = new Bars(30, 0.01, 1, 200);
Bars test2 = new Bars(0, 0.01, -1, 100);
Bars rest = new Bars(1, 0.00, -1, 50);
int w = width/2;
int h = height/2;

void setup() {
  size(700,600);//fullScreen();//size(200, 200);
  w = width/2;
  h = height/2;
  //frameRate(30);
  colorMode(HSB, 100, 100, 100, 100);
  background(100);
  stroke(0,0,0,0);
  t0=millis();
  startTime = millis(); 
  test1.Init();
  test2.Init();
}

void draw() {
  t1 = millis();
  t0 = t1;
  if (counter == 0) { Set(test1, 30, 0.01, 1);}
  if (counter == 2) { Set(test1, 10, 0.03, -1);} 
  if (counter == 4) { Set(test1, 6, 0.01, 1);} 
  if (counter == 6) { Set(test1, 6, 0.01, -1);} 

  
  background(100);
  stroke(0,0,0,0);
  fill(0);
  //triangle(width/2,height/2,5,5,-10,10);
  if(tick==true){
    test1.update();
    test2.update();
  }
  else if(tick==false){
    fill(100,0,50, 100);
    rect(0,0,width,height);
  }
  if(t1 - startTime >= wait){
    tick = !tick;
    startTime = t1;
    counter = counter + 1;
  } 
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
  fill(100,0,50, alpha);
  rect(0,0,width,height);
  
}
void Set(Bars _bars, int _numBars, float _Vel, int _Dir) {
  _bars.NUMBER_OF_THINGS = _numBars;
  _bars.vel = _Vel;
  _bars.dir = _Dir;
  _bars.Reset();
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
  
//  private void coords(int radius, int degrees){
//    int x = (int)(cos(degrees) * radius);
//    int y = (int)(sin(degrees) * radius);
//    return x, y }
    
  
  public void Reset(){
    Init();
  }
  
  private void Init() {
    barList = new Bar[NUMBER_OF_THINGS];
    for (int i=0; i< barList.length; i++){
      float rotation = i* TWO_PI / (NUMBER_OF_THINGS);
      barList[i] = new Bar(rotation, TWO_PI / (NUMBER_OF_THINGS), vel*dir);
    }
  }
  void update() { 
    for (int i=0; i< NUMBER_OF_THINGS; i++){
      barList[i].renew(barList[i].ROTATION + barList[i].VEL);
      
      fill(0,0,0,barList[i].COLOUR);
      triangle(w, h, barList[i].X1 + w, barList[i].Y1 + h, barList[i].X2 + w, barList[i].Y2 + h);
      

    }
  }

  
class Bar {
  float X1, Y1, X2, Y2, ROTATION;
  float COLOUR, _DEGREES, VEL;
  
  Bar(float rotation, float degrees, float vel) {
    this.X1 = (cos(rotation)*width);
    this.Y1 = (sin(rotation)*width);
    this.X2 = (cos(rotation+(degrees))*width);
    this.Y2 = (sin(rotation+(degrees))*width);
    this.COLOUR = random(50,95);  
    this.ROTATION = rotation;
    this._DEGREES = degrees;
    this.VEL = vel;
  }
  
  void renew(float rotation) {
    this.X1 = (cos(rotation)*width);
    this.Y1 = (sin(rotation)*width);
    this.X2 = (cos(rotation+(_DEGREES/2))*width);
    this.Y2 = (sin(rotation+(_DEGREES/2))*width);
    this.ROTATION = rotation;
  }
}
}