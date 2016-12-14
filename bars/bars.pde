
int t0;
int t1;
int startTime;
boolean tick = false;
int wait = 1*10*1000;
int counter = 0;
int WIDTH;
int HEIGHT;
int alpha = 0;
int fadeTime = 1000;


  
Bars test1 = new Bars(10, 0, 0, 1, 0, 100);
Bars rest1 = new Bars(1, 0, 0, 1, 1, 50);


void setup() {
  size(700,600);//fullScreen();
  WIDTH = width;
  HEIGHT = height;
  println(WIDTH, HEIGHT);
  //size(800,800);
  colorMode(HSB, 100, 100, 100, 100);
  background(100);
  stroke(0,0,0,0);
  t0=millis();
  startTime = millis();  
  test1.Init();
  rest1.Init();
}



void draw() {
  t1=millis();
  t0=t1;
  if (counter == 0) { Set(test1, 10, 8, 0, 1, 0);}
  if (counter == 2) { Set(test1, 10, -8, 0, 1, 0);} 
  if (counter == 4) { Set(test1, 6, 0, 8, 0, 1);} 
  if (counter == 6) { Set(test1, 6, 0, -8, 0, 1);} 
  background(100);
  if(tick == true){
    test1.update();  
  }

  else if(tick==false){
    
    rest1.update(); 
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
  
  
  //println(alpha);
  fill(100,0,50, alpha);
  rect(0,0,width,height);

}

void Set(Bars _bars, int _numBars, int _VelX, int _VelY, int _DirX, int _DirY) {
  _bars.NUMBER_OF_THINGS = _numBars;
  _bars.velX = _VelX;
  _bars.velY = _VelY;
  _bars.dirX = _DirX;
  _bars.dirY = _DirY;
  _bars.Reset();
}

public class Bars { 
  int NUMBER_OF_THINGS;
  int velX;  // speed and direction in x
  int velY; // speed and direction in y
  int dirX;  // make 1 to move in x
  int dirY; // make 1 to move in y
  int COLOUR;
  float fade;
  int myFrameCount;
  float[] x = new float[NUMBER_OF_THINGS+1];
  float[] y = new float[NUMBER_OF_THINGS+1];
      
  
  public Bars(int numBars, int _velX, int _velY, int _dirX, int _dirY, int colour) {     
    NUMBER_OF_THINGS = numBars; 
    velX = _velX;
    velY = _velY;
    dirX = _dirX;
    dirY = _dirY;
    COLOUR = colour;
    x = new float[NUMBER_OF_THINGS+1];
    y = new float[NUMBER_OF_THINGS+1];
    //Init();
  }
  
  public void Reset(){
    float[] x = new float[NUMBER_OF_THINGS+1];
    float[] y = new float[NUMBER_OF_THINGS+1];
    Init();
  }
  
  private void Init() {
    for (int i=0; i< (NUMBER_OF_THINGS+1); i++){
      x[i] = (WIDTH / NUMBER_OF_THINGS) * (i) * dirX;
      y[i] = (HEIGHT / NUMBER_OF_THINGS) * (i) * dirY;  
      //println(x[i], width, WIDTH);
    }
  }
      
  void update() { 
    //size(800,800);//fullScreen();
    fill(0, 0,0, COLOUR);
      
    for (int i=0; i< NUMBER_OF_THINGS+1; i++){

      rect(x[i], y[i], (WIDTH / (2*NUMBER_OF_THINGS) + dirY*WIDTH), (HEIGHT / (2*NUMBER_OF_THINGS)+ dirX*height));
      
      //println(x[i], width);
      x[i] = x[i] + velX;
      y[i] = y[i] + velY;
      if (x[i]>WIDTH){ x[i]=0 - (WIDTH / (NUMBER_OF_THINGS));}
      if (y[i]>HEIGHT){ y[i]= 0 - (HEIGHT / (NUMBER_OF_THINGS));}
      if (y[i]<(0 - (HEIGHT / (NUMBER_OF_THINGS)))) { y[i]=HEIGHT;}
      if (x[i]<(0 - (WIDTH / (NUMBER_OF_THINGS)))) { x[i]=WIDTH;}


    }
  }

}