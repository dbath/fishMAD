package processing.test.flow;

import processing.core.*; 
import processing.data.*; 
import processing.event.*; 
import processing.opengl.*; 

import java.util.HashMap; 
import java.util.ArrayList; 
import java.io.File; 
import java.io.BufferedReader; 
import java.io.PrintWriter; 
import java.io.InputStream; 
import java.io.OutputStream; 
import java.io.IOException; 

public class flow extends PApplet {


//float x = random(0,width);
//float y = random(0,height);

int NUMBER_OF_THINGS = 500;
int THING_SIZE = 40;
int velX = 20;  // speed and direction in x
int velY = 0; // speed and direction in y
float varX = 2; // variation in x
float varY = 2; //variation in y

float[] x = new float[NUMBER_OF_THINGS];
float[] y = new float[NUMBER_OF_THINGS];
float[] _varX = new float[NUMBER_OF_THINGS];
float[] _varY = new float[NUMBER_OF_THINGS];

public void setup() {
  
  //size(500,400);
  colorMode(HSB, 100,100,100,100);
  background(100);
  for (int i=0; i< NUMBER_OF_THINGS; i++){
    x[i] = random(0,width);
    y[i] = random(0,height);
    _varX[i] = random(-1.0f*varX, varX);
    _varY[i] = random(-1.0f*varY, varY);
    
  }
  
}

public void draw() {
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
}
  public void settings() {  fullScreen(2); }
  static public void main(String[] passedArgs) {
    String[] appletArgs = new String[] { "flow" };
    if (passedArgs != null) {
      PApplet.main(concat(appletArgs, passedArgs));
    } else {
      PApplet.main(appletArgs);
    }
  }
}
