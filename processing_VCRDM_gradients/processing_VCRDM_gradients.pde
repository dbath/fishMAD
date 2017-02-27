
//float x = random(0,width);
//float y = random(0,height);

int NUMBER_OF_THINGS = 18;
int THING_SIZE = 25;
int multi = 20;
float velX = 1;  // speed and direction in x
float velY = -6; // speed and direction in y
float varX = 7; // variation in x
float varY = 7; //variation in y

float[] x = new float[NUMBER_OF_THINGS];
float[] y = new float[NUMBER_OF_THINGS];
float[] _varX = new float[NUMBER_OF_THINGS];
float[] _varY = new float[NUMBER_OF_THINGS];

void setup() {
  fullScreen();
  //size(1600,1000);
  colorMode(HSB, 100,100,100,1000);
  background(100);
  stroke(0,0,0,0);
  randomSeed(3);
  for (int i=0; i< NUMBER_OF_THINGS; i++){
    x[i] = random(0,width);
    y[i] = random(0,height);
    _varX[i] = random(-1.0*varX, varX);
    _varY[i] = random(-1.0*varY, varY);
    
  }
  
}

void draw() {
  background(100);
  //stroke(0,0,0);
  //fill(200,200,0);
  for (int i=0; i< NUMBER_OF_THINGS; i++){
    
    drawGradient(x[i], y[i], THING_SIZE, THING_SIZE);
    x[i] = x[i] + velX + _varY[i];
    y[i] = y[i] + velY + _varX[i];
    if (x[i]>(width+THING_SIZE*multi/3)){ x[i]=0- THING_SIZE*multi/3;}
    if (y[i]>(height+THING_SIZE*multi/3)){ y[i]=0-THING_SIZE*multi/3;}
    if (y[i]<(0-THING_SIZE*multi/3)){ y[i]=(height+(THING_SIZE*multi/3));}
    if (x[i]<(0-THING_SIZE*multi/3)){ x[i]=(width+(THING_SIZE*multi/3));}
  }
}

void drawGradient(float x, float y, float radius, float colour) {
  float h = 1;//colour;
  for (float r = radius; r > 0; --r) {
    fill(0,0,0,h);
    ellipse(x, y, multi*r, multi*r);
    h = h + sqrt(4*h);
  }
}