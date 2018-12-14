import spout.*;

// PImage keeps alpha channel intact, unlike other drawing methods in Processing
PGraphics data;

int squaring_bar;
int checkerSize = 50;
int screenSize = 1280;//displayHeight;
float gridsize;

Spout spout;
void setup(){
  stroke(0,0,0,0);
  fill(0,0,0,100);
  size(3,3,P2D);
  data = createGraphics(screenSize, screenSize);
  
  //fullScreen();
  ellipseMode(CENTER);
  gridsize = 0.5*screenSize - 100;
  squaring_bar = 0;//(screenSize - screenSize) /2;
  spout = new Spout(this);
  spout.createSender("Align Processing");

}
void draw(){
  data.beginDraw();
  data.colorMode(HSB, 100,100,100,100);
  data.background(0,0,100,100);
  //print(screenSize); print(screenSize);
  data.rect(0,0,squaring_bar, screenSize);
  data.rect(screenSize - squaring_bar,0,squaring_bar, screenSize);
  data.rect((screenSize/2)-3, 0, 6, screenSize);
  data.rect(0, (screenSize/2)-3, screenSize, 6);
  //rect(0, 0, screenSize/2, screenSize/2);
  checkerBoard((squaring_bar) +50, 50, 0.5*screenSize-100,0.5*screenSize-100, 8);
  checkerBoard((squaring_bar) +50, screenSize/2 + 50, 0.5*screenSize-100, 0.5*screenSize-100, 16);
  checkerBoard((screenSize/2) +50, 50, 0.5*screenSize-100, 0.5*screenSize-100, 32);
  checkerBoard((screenSize/2) +50, screenSize/2 + 50, 0.5*screenSize-100, 0.5*screenSize-100, 64);
  data.fill(75,20,100,100);
  data.stroke(0,0,0,100);
  data.ellipse(squaring_bar + screenSize/4, screenSize/4, 20, 20);
  data.ellipse(squaring_bar + screenSize/4, 3*screenSize/4, 20, 20);
  data.ellipse(screenSize/2 + screenSize/4, screenSize/4, 20, 20);
  data.ellipse(screenSize/2 + screenSize/4, 3*screenSize/4, 20, 20);
  data.ellipse(screenSize/2, screenSize/2, 20, 20);
  data.fill(0,0,0,100);
  data.ellipse(squaring_bar + screenSize/4, screenSize/4, 5, 5);
  data.ellipse(squaring_bar + screenSize/4, 3*screenSize/4, 5, 5);
  data.ellipse(screenSize/2 + screenSize/4, screenSize/4, 5, 5);
  data.ellipse(screenSize/2 + screenSize/4, 3*screenSize/4, 5, 5);
  data.ellipse(screenSize/2, screenSize/2, 5, 5);
  data.endDraw();
  spout.sendTexture(data);

}



void checkerBoard(int X, int Y, float W, float H, int numRows){
  //int numRows = floor(H/S);
  float S = (H/numRows);
  if (numRows%2==1){ numRows = numRows - 1;}
  for (int i=0; i< (numRows/2); i++){
    for (int j=0; j< numRows; j++){
      float xpos = X  + j*S;
      float ypos = Y  + 2*i*S;
      if (j%2==0){
        data.rect(xpos, ypos, S, S);
      }
      else {
        data.rect(xpos, ypos + S, S, S);
      }
      
    }


}
}
