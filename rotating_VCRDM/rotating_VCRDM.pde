
int THING_SIZE = 50;
float SPEED = 0.2;
int t0;
int t1;
int startTime;
boolean tick = false;
int wait = 1*5*1000;
int counter = 0;
Dots test1 = new Dots(0.5, 500, -1.0*SPEED); 
Dots test2 = new Dots(1.0, 100, 1.0*SPEED); 
Dots rest1 = new Dots(0.5, 00, -1.0*SPEED); 
Dots rest2 = new Dots(1.0, 00, 1.0*SPEED); 


void setup() 
{
  fullScreen();//size(200, 200);
  //frameRate(30);
  colorMode(HSB, 100, 100, 100, 100);
  background(100);
  stroke(0,0,0,0);
  t0=millis();
  startTime = millis();
  //doit();
}


void draw() { 
  t1=millis();
  int fps = (int)(1000./((float)(t1-t0)));
  t0=t1;
  
  if (counter == 0) { set_C(test1, test2, 500, 100);}
  if (counter == 2) { set_C(test1, test2, 0, 600);}
  if (counter == 4) { set_C(test1, test2, 300, 300);}
  if (counter == 6) { set_C(test1, test2, 600, 000);}
  if (counter == 8) { set_C(test1, test2, 150, 450);}
  
  if(t1 - startTime >= wait){
    tick = !tick;
    startTime = t1;
    counter = counter + 1;
  }
  if (frameCount % 50 == 0){
    println(test1.NUMBER_OF_THINGS);
  }
  background(100);
  translate(width/2, height/2);
  
  
  if(tick == true){
    test1.update(); 
    test2.update(); 
  }
  else if(tick==false){
    rest1.update(); 
    rest2.update(); 
  }
  
  translate(-width/2, -height/2);
  fill(0,100,100,100);
  textSize(100);
  //text(str(fps),width/2, height/2);
  //text(str(tick),width/2, height/2);
  
} 

void set_C(Dots group1, Dots group2, int num1, int num2) {
  group1.NUMBER_OF_THINGS = num1;
  group2.NUMBER_OF_THINGS = num2;
  group1.Reset();
  group2.Reset();
}
 
void doit(){
 for (int i=0; i < 20; i++) {
  fill(0,100,100,100);
  textSize(200);
  text("FOOBAR",width/2, height/2);
  //delay(2000);
  } 
  
}
 
public class Dots { 
  int NUMBER_OF_THINGS;
  float ORDER;
  float DIR; 
  Dot[] dotList;    
  
  public Dots(float order, int numDots, float direction) {     
    NUMBER_OF_THINGS = numDots; 
    DIR = direction; 
    ORDER = order;
    Init();
  }
  
  public void Reset(){
    Init();
  }
  
  private void Init() {
    //Dot[] dotList; 
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
      
      if (abs(dotList[i].X) > 1*width){ dotList[i].refresh() ;}
      if (abs(dotList[i].Y) > 1*height){ dotList[i].refresh() ;}
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
    this.X=random(-2*width, 2*width);
    this.Y = random(-2*height, 2*height);
    this.COLOUR = random(80);
    this.VELX = random(-0.125,0.125); 
    this.VELY = random(-0.125,0.125);   
  }
  
  void refresh(){
    X=random(-1*width, 1*width);
    Y = random(-1*height, 1*height);
    COLOUR = random(80);
    VELX = random(-0.125,0.125);
    VELY = random(-0.125,0.125);
  }
  
  
}