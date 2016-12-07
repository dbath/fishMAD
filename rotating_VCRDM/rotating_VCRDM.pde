
int THING_SIZE = 50;
float SPEED = 0.2;
Dots first = new Dots(0.5, 65, -1.0*SPEED); 
Dots second = new Dots(1.0, 135, 1.0*SPEED); 


void setup() 
{
  fullScreen();//size(200, 200);
  //frameRate(30);
  colorMode(HSB, 100, 100, 100, 100);
  background(100);
  stroke(0,0,0,0);
}


void draw() { 
  background(100);
  translate(width/2, height/2);
  first.update(); 
  second.update();  
  translate(-width/2, -height/2);
} 
 
class Dots { 
  int NUMBER_OF_THINGS;
  float ORDER;
  float DIR; 
  float[] x;
  float[] y;
  float[] colour;
  float[] velocities;
  Dots (float order, int numDots, float direction) { 
    NUMBER_OF_THINGS = numDots; 
    DIR = direction; 
    ORDER = order;
    x = new float[NUMBER_OF_THINGS];
    y = new float[NUMBER_OF_THINGS];
    colour = new float[NUMBER_OF_THINGS];
    velocities = new float[NUMBER_OF_THINGS];
    for (int i=0; i < NUMBER_OF_THINGS; i++) {
      //x[i] = random(-8*width, 8*width);
      //y[i] = random(-8*height, 8*height);
      //colour[i] = random(80);
      x[i], y[i], colour[i], velocities[i] = generate_dot();
      x[i] = x[i] + velocities[i];
      y[i] = y[i] + velocities[i];
      if (x[i] > 8*width){ x[i], y[i], colour[i], velocities[i] = generate_dot();}
      if (y[i] > 8*height){ x[i], y[i], colour[i], velocities[i] = generate_dot();}
      if (x[i] < -8*width){ x[i], y[i], colour[i], velocities[i] = generate_dot();}
      if (y[i] < -8*height){ x[i], y[i], colour[i], velocities[i] = generate_dot();}
      
      
      
      Dot d = new Dot();
      
      d.X = d.X + d.VEL;
      d.Y = 
      x[i] = x[i] + velocities[i];
      y[i] = y[i] + velocities[i];
      if (x[i] > 8*width){ x[i], y[i], colour[i], velocities[i] = generate_dot();}
      if (y[i] > 8*height){ x[i], y[i], colour[i], velocities[i] = generate_dot();}
      if (x[i] < -8*width){ x[i], y[i], colour[i], velocities[i] = generate_dot();}
      if (y[i] < -8*height){ x[i], y[i], colour[i], velocities[i] = generate_dot();}
      
    }
  } 
  void update() { 
    rotate(ORDER*DIR*radians(frameCount));
    for (int i=0; i< NUMBER_OF_THINGS; i++){
      fill(0, 0,0, colour[i]);
      ellipse(x[i], y[i], THING_SIZE, THING_SIZE);
    }
  }

}

Class Dot {
  int X, Y;
  float COLOUR, VEL;
  
  Dot() {
    this.X=random(-8*width, 8*width);
    this.Y = random(-8*height, 8*height);
    this.COLOUR = random(80);
    this.VEL = random(0,2);    
  }
  
}