
//float x = random(0,width);
//float y = random(0,height);

int NUMBER_OF_THINGS = 400;
int THING_SIZE = 50;
int velX = 10;  // speed and direction in x
int velY = 2; // speed and direction in y
float varX = 2; // variation in x
float varY = 2; //variation in y

float[] x = new float[NUMBER_OF_THINGS];
float[] y = new float[NUMBER_OF_THINGS];
float[] _varX = new float[NUMBER_OF_THINGS];
float[] _varY = new float[NUMBER_OF_THINGS];

void setup() {
  fullScreen();
  //size(500,400);
  colorMode(HSB, 100);
  background(100);
  for (int i=0; i< NUMBER_OF_THINGS; i++){
    x[i] = random(0,width);
    y[i] = random(0,height);
    _varX[i] = random(-1.0*varX, varX);
    _varY[i] = random(-1.0*varY, varY);
    
  }
  
}

void draw() {
  background(100);
  stroke(0,0,0);
  fill(200,200,0);
  for (int i=0; i< NUMBER_OF_THINGS; i++){
    
    ellipse(x[i], y[i], THING_SIZE, THING_SIZE);
    x[i] = x[i] + velX + _varY[i];
    y[i] = y[i] + velY + _varX[i];
    if (x[i]>width){ x[i]=0;}
    if (y[i]>height){ y[i]=0;}
    if (y[i]<0){ y[i]=height;}
    if (x[i]<0){ x[i]=width;}
  }
}