
int squaring_bar;
int checkerSize = 50;
int screenSize = displayHeight;
float gridsize = 0.5*height - 100;
void setup(){
  colorMode(HSB, 100,100,100,100);
  stroke(0,0,0,0);
  fill(0,0,0,100);
  //size(displayHeight, displayHeight);
  
  fullScreen();
  ellipseMode(CENTER);
  squaring_bar = (width - height) /2;


  background(0,0,100,100);
  rect(0,0,squaring_bar, height);
  rect(width - squaring_bar,0,squaring_bar, height);
  rect((width/2)-3, 0, 6, height);
  rect(0, (height/2)-3, width, 6);
  //rect(0, 0, width/2, height/2);
  checkerBoard((squaring_bar) +50, 50, 0.5*height-100,0.5*height-100, 8);
  checkerBoard((squaring_bar) +50, height/2 + 50, 0.5*height-100, 0.5*height-100, 16);
  checkerBoard((width/2) +50, 50, 0.5*height-100, 0.5*height-100, 32);
  checkerBoard((width/2) +50, height/2 + 50, 0.5*height-100, 0.5*height-100, 64);
  fill(75,20,100,100);
  stroke(0,0,0,100);
  ellipse(squaring_bar + height/4, height/4, 20, 20);
  ellipse(squaring_bar + height/4, 3*height/4, 20, 20);
  ellipse(width/2 + height/4, height/4, 20, 20);
  ellipse(width/2 + height/4, 3*height/4, 20, 20);
  fill(0,0,0,100);
  ellipse(squaring_bar + height/4, height/4, 5, 5);
  ellipse(squaring_bar + height/4, 3*height/4, 5, 5);
  ellipse(width/2 + height/4, height/4, 5, 5);
  ellipse(width/2 + height/4, 3*height/4, 5, 5);



}

void draw(){
  
  
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
        rect(xpos, ypos, S, S);
      }
      else {
        rect(xpos, ypos + S, S, S);
      }
      
    }


}
}