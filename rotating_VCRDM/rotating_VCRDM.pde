
int THING_SIZE = 50;
float SPEED = 0.2;
int t0;
Dots first = new Dots(0.5, 500, -1.0*SPEED); 
Dots second = new Dots(1.0, 100, 1.0*SPEED); 


void setup() 
{
  fullScreen();//size(200, 200);
  //frameRate(30);
  colorMode(HSB, 100, 100, 100, 100);
  background(100);
  stroke(0,0,0,0);
  t0=millis();
}


void draw() { 
  int t1=millis();
  int fps = (int)(1000./((float)(t1-t0)));
  t0=t1;
  background(100);
  translate(width/2, height/2);
  first.update(); 
  second.update();  
  translate(-width/2, -height/2);
  fill(0,100,100,100);
  textSize(100);
  text(str(fps),width/2, height/2);
  
} 
 
class Dots { 
  int NUMBER_OF_THINGS;
  float ORDER;
  float DIR; 
  Dot[] dotList;
  Dots (float order, int numDots, float direction) { 
    NUMBER_OF_THINGS = numDots; 
    DIR = direction; 
    ORDER = order;
    dotList = new Dot[NUMBER_OF_THINGS];
    for (int i=0; i < dotList.length; i++) {
      dotList[i] = new Dot();      
    }
  } 
  
  void update() { 
    rotate(ORDER*DIR*radians(frameCount));
    for (int i=0; i< NUMBER_OF_THINGS; i++){
      dotList[i].X = dotList[i].X + dotList[i].VELX;
      dotList[i].Y = dotList[i].Y + dotList[i].VELY;
      
      if (abs(dotList[i].X) > 8*width){ dotList[i].refresh() ;}
      if (abs(dotList[i].Y) > 8*height){ dotList[i].refresh() ;}
      //if (abs(dotList[i].X) > 8*width){ dotList[i].refresh() ;}
      //if (abs(dotList[i].Y) > 8*height){ dotList[i].refresh() ;}
      
      
      fill(0, 0,0, dotList[i].COLOUR);
      ellipse(dotList[i].X, dotList[i].Y, THING_SIZE, THING_SIZE);
      
      
      
      
    }
  }

}

class Dot {
  float X, Y;
  float COLOUR, VELX, VELY;
  
  Dot() {
    this.X=random(-12*width, 12*width);
    this.Y = random(-12*height, 12*height);
    this.COLOUR = random(80);
    this.VELX = random(-0.125,0.125); 
    this.VELY = random(-0.125,0.125);   
  }
  
  void refresh(){
    X=random(-8*width, 8*width);
    Y = random(-8*height, 8*height);
    COLOUR = random(80);
    VELX = random(-0.125,0.125);
    VELY = random(-0.125,0.125);
  }
  
  
}