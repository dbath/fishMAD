
//float x = random(0,width);
//float y = random(0,height);

int NUMBER_OF_THINGS = 1000;
int THING_SIZE = 20;
int velX = -10;  // speed and direction in x
int velY = 0; // speed and direction in y
float varX = 1; // variation in x
float varY = 1; //variation in y

float[] x = new float[NUMBER_OF_THINGS];
float[] y = new float[NUMBER_OF_THINGS];
float[] _varX = new float[NUMBER_OF_THINGS];
float[] _varY = new float[NUMBER_OF_THINGS];

void setup() {
  fullScreen();
  //size(500,400);
  colorMode(HSB, 100,100,100,100);
  background(100);
  for (int i=0; i< 1000; i++){
    x[i] = random(0,width);
    y[i] = random(0,height);
    _varX[i] = random(-1.0,1.0);
    _varY[i] = sqrt(1 - pow(_varX[i],2)) * pow(-1.0, int(random(0,100)));   //random(-1.0*varY, varY);

  } 
}

void draw() {
  background(00,00,100,100);
  stroke(0,41,100,0);
  fill(0,100,00,100);
  for (int i=0; i<400; i++){
    int I = round(random(0,NUMBER_OF_THINGS-1));
    x[I] = random(0,width);
    y[I] = random(0,height);
  
  }
  for (int i=0; i< 30; i++){
    
    ellipse(x[i], y[i], THING_SIZE, THING_SIZE);
    x[i] = x[i] + velX + _varX[i];
    y[i] = y[i] + velY + _varY[i];
    if (x[i]>width){ x[i]=0;}
    if (y[i]>height){ y[i]=0;}
    if (y[i]<0){ y[i]=height;}
    if (x[i]<0){ x[i]=width;}
  }
  for (int i=31; i< 1000; i++){
    
    ellipse(x[i], y[i], THING_SIZE, THING_SIZE);
    x[i] = x[i] +  _varX[i] +_varX[i]*velX;//+ cos(_varX[i]/_varY[i])*velX;//sqrt(pow(velX,2) - pow(_varX[i],2));
    y[i] = y[i] +  _varY[i] +_varY[i]*velX;//+ sin(_varX[i]/_varY[i])*velX;// sqrt(pow(velX,2) - pow(_varY[i],2));
    if (x[i]>width){ x[i]=0;}
    if (y[i]>height){ y[i]=0;}
    if (y[i]<0){ y[i]=height;}
    if (x[i]<0){ x[i]=width;}
  }
  
  saveFrame("video_L03/stim-######.png");
}