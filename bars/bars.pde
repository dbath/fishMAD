
//float x = random(0,width);
//float y = random(0,height);

int NUMBER_OF_THINGS = 10;
int velX = -5;  // speed and direction in x
int velY = 0; // speed and direction in y
int dirX = 1;  // make 1 to move in x
int dirY = 0; // make 1 to move in y


float[] x = new float[NUMBER_OF_THINGS+1];
float[] y = new float[NUMBER_OF_THINGS+1];

void setup() {
  fullScreen();
  //size(500,400);
  colorMode(HSB, 100);
  background(100);
  for (int i=0; i< (NUMBER_OF_THINGS+1); i++){
    x[i] = width / NUMBER_OF_THINGS * (i-1) * dirX;
    y[i] = height / NUMBER_OF_THINGS * (i-1) * dirY;
    
  }
  
}

void draw() {
  background(100);
  stroke(0,0,0);
  fill(0,0,0);
  for (int i=0; i< NUMBER_OF_THINGS+1; i++){
    rect(x[i], y[i], (width / (2.0*NUMBER_OF_THINGS) + dirY*width), (height / (2.0*NUMBER_OF_THINGS)+ dirX*height));
    
    x[i] = x[i] + velX;
    y[i] = y[i] + velY;
    if (x[i]>width){ x[i]=0 - (width / (NUMBER_OF_THINGS));}
    if (y[i]>height){ y[i]= 0 - (height / (NUMBER_OF_THINGS));}
    if (y[i]<(0 - (height / (NUMBER_OF_THINGS)))) { y[i]=height;}
    if (x[i]<(0 - (width / (NUMBER_OF_THINGS)))) { x[i]=width;}
  }
}