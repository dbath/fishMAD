int startTime;
int t1;
int t0;


void setup(){
  fullScreen();
  colorMode(HSB, 100, 100, 100, 100);
  background(100);
  stroke(0,0,0,0);
  textSize(100);
  startTime = millis();
  t0 = millis();
}

void draw() {
  t1 = millis();
  int fps = (int)(1000./((float)(t1-t0)));
  t0=t1;
  background(100);
  fill(0,100,100,100);
  text((t1 - startTime), width/2, height/2);
  text((fps), width/2, height/3);
  
}
  