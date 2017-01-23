
//float x = random(0,width);
//float y = random(0,height);

int NUMBER_OF_THINGS = 3000;
int THING_SIZE = 25;
int rotation = 1; // rotation speed
float COHERENCE = 0.7;
float[] x = new float[NUMBER_OF_THINGS];
float[] y = new float[NUMBER_OF_THINGS];
float[] r = new float[NUMBER_OF_THINGS];
float[] colour = new float[NUMBER_OF_THINGS];
float[] direction = new float[NUMBER_OF_THINGS];

void setup() {
  fullScreen();
  //size(500,400);
  colorMode(HSB, 100, 100, 100, 100);
  background(100);
  for (int i=0; i< NUMBER_OF_THINGS; i++){
    x[i] = random(-0.5*width, 1.5*width);
    y[i] = random(-0.5*height, 1.5*height);
    colour[i] = random(80);
    float rando = (float)random(0,1);
    if (rando > COHERENCE) {
      direction[i] = -1;
    }
    else { direction[i] = 1;
    }
    //r[i] = (int)(sqrt( sq(x[i] - (float)(width/2.0)) + sq(y[i] - (float)(height/2.0))));
  }
  
}

void draw() {
  background(100);
  stroke(0,0,0,0);
  //fill(200,200,0);
  translate(width/2, height/2);
  rotate(radians(frameCount));
  translate(-width/2, -height/2);
  for (int i=0; i< NUMBER_OF_THINGS; i++){
    //float t = millis()/1000.0f;
    //int cx = (int)(x[i] + r[i]*cos(t)); 
    //int cy = (int)(y[i] + r[i]*sin(t));
    fill(0, 0,0, colour[i]);
    ellipse(x[i], y[i], THING_SIZE, THING_SIZE);
    //if (x[i]>width){ x[i]=0;}
    //if (y[i]>height){ y[i]=0;}
    //if (y[i]<0){ y[i]=height;}
    //if (x[i]<0){ x[i]=width;}
  }
}