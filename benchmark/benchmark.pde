int startTime;
int t1;
int t0;

int NUMBER_OF_THINGS = 500;
int THING_SIZE = 40;
int velX = 00;  // speed and direction in x
int velY = -20; // speed and direction in y
float varX = 2; // variation in x
float varY = 2; //variation in y

float[] x = new float[NUMBER_OF_THINGS];
float[] y = new float[NUMBER_OF_THINGS];
float[] _varX = new float[NUMBER_OF_THINGS];
float[] _varY = new float[NUMBER_OF_THINGS];


void setup(){
  fullScreen();
  colorMode(HSB, 100, 100, 100, 100);
  background(100);
  stroke(0,0,0,0);
  textSize(100);
  startTime = millis();
  t0 = millis();
  for (int i=0; i< NUMBER_OF_THINGS; i++){
    x[i] = random(0,width);
    y[i] = random(0,height);
    _varX[i] = random(-1.0*varX, varX);
    _varY[i] = random(-1.0*varY, varY);
    
  }


}

void draw() {
  t1 = millis();
  int fps = (int)(1000./((float)(t1-t0)));
  t0=t1;
  background(00,00,100,100);
  stroke(0,41,100,0);
  fill(0,100,00,100);
  for (int i=0; i< NUMBER_OF_THINGS; i++){
    
    ellipse(x[i], y[i], THING_SIZE, THING_SIZE);
    x[i] = x[i] + velX + _varY[i];
    y[i] = y[i] + velY + _varX[i];
    if (x[i]>width){ x[i]=0;}
    if (y[i]>height){ y[i]=0;}
    if (y[i]<0){ y[i]=height;}
    if (x[i]<0){ x[i]=width;}
  }
  fill(0,100,100,100);
  text((t1 - startTime), width/2, height/2);
  text((fps), width/2, height/3);
  
}
  