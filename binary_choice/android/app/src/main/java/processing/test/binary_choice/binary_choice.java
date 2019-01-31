package processing.test.binary_choice;

import processing.core.*; 
import processing.data.*; 
import processing.event.*; 
import processing.opengl.*; 

import java.io.FileWriter; 
import java.io.*; 
import java.util.*; 
import java.math.BigDecimal; 
import java.text.DecimalFormat; 
import java.time.Instant; 
import java.sql.Timestamp; 
import java.util.Collections; 
import controlP5.*; 

import java.util.HashMap; 
import java.util.ArrayList; 
import java.io.File; 
import java.io.BufferedReader; 
import java.io.PrintWriter; 
import java.io.InputStream; 
import java.io.OutputStream; 
import java.io.IOException; 

public class binary_choice extends PApplet {




//-------------------------- DO NOT CHANGE VALUES ABOVE------------------------------------


float stimDelay = 3.0f; //delay between pressing "go" and presentation of stimulus
float stimDuration = 3.0f; //duration of stimulus presentation in seconds 

float dotSize = 0.1f;  // size of dots in proportion of screen height (eg 0.5 will be half the height of the screen)
float dotPosX = 0.4f; //horizontal distance of dots from centre, in proportion of screen height
float dotPosY = 0.5f; //vertical distance of dots from top, in proportion of screen height

int defaultBkgColour = 50; //default colour of background from 0 (red) to 100 (red) ROYGBIVR
int defaultBkgBrightness = 100; //default brightness of background from 0 (black) to 100 (white)
int defaultBkgSaturation = 0; //default colour of background from 0 (black) to 100 (white)

int defaultDotColour_R = 33; //default colour of dots from 0 (red) to 100 (red) ROYGBIVR
int defaultDotBrightness_R = 100; //default colour of dots from 0 (black) to 100 (bright)
int defaultSaturation_R = 100; //default colour of dots from 0 (black) to 100 (white)

int defaultDotColour_L = 0; //default colour of dots from 0 (red) to 100 (red) ROYGBIVR
int defaultDotBrightness_L = 100; //default colour of dots from 0 (black) to 100 (white)
int defaultSaturation_L = 100; //default colour of dots from 0 (black) to 100 (white)


//-------------------------- DO NOT CHANGE VALUES BELOW------------------------------------












//GUI Setup


ControlP5 cP5;
Slider abc;
boolean goNoGo = false;
boolean SETUP = false;
//Logging setup
FileWriter fw;
BufferedWriter bw;
DecimalFormat formatter = new DecimalFormat("###.#");


int t0;
int tLoop;
float alpha = 100;
int hideMode = 0;
float stopgo = 1.0f;
int DIRECTION = 1;
boolean running = false;
//Drawing variables
int sqBar; 
int RANDO = 1;

int bkgColour;
int dotColour_R;
int dotColour_L;
int bkgBrightness;
int dotBrightness_R;
int dotBrightness_L;
int bkgSaturation;
int dotSaturation_R;
int dotSaturation_L;
boolean showDots = false;
boolean NEWFILE = true;
String HEADERS = "TIME" 
                + '\t' + "BKGCOLOUR" 
                + '\t' + "BKGBRIGHTNESS"
                + '\t' + "BKGSAT" 
                + '\t' + "DOTCOLOUR_1" 
                + '\t' + "DOTBRIGHTNESS_1" 
                + '\t' + "DOTSAT_1" 
                + '\t' + "DOTCOLOUR_2" 
                + '\t' + "DOTBRIGHTNESS_2" 
                + '\t' + "DOTSAT_2" 
                + '\t' + "DOTSIZE" 
                + '\t' + "DOTPOSX" 
                + '\t' + "DOTPOSY" 
                + '\t' + "RANDOMIZATION"      
                + '\t' + "ACTION" 
                + '\n';

public void setup(){

  
  println(str(height) + '\t' + str(width));
  colorMode(HSB, 100,100,100,100);
  
  ellipseMode(CENTER);
  
  //adjust sizing relative to screen size:
  
  sqBar = (width - height) /2;
  
  int H = PApplet.parseInt(0.03f*height);
  
  // setup GUI
  cP5 = new ControlP5(this);
  
  cP5.addSlider("bkgColour")
     .setPosition(PApplet.parseInt(0.5f*sqBar),1*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultBkgColour)
     ;
    cP5.addSlider("dotColour_R")
     .setPosition(PApplet.parseInt(0.5f*sqBar),5*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultDotColour_R)
     ;  
    cP5.addSlider("dotColour_L")
     .setPosition(PApplet.parseInt(0.5f*sqBar),9*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultDotColour_L)
     ;  
    cP5.addSlider("bkgBrightness")
     .setPosition(PApplet.parseInt(0.5f*sqBar),3*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultBkgBrightness)
     ;
    cP5.addSlider("dotBrightness_R")
     .setPosition(PApplet.parseInt(0.5f*sqBar),7*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultDotBrightness_R)
     ;  
    cP5.addSlider("dotBrightness_L")
     .setPosition(PApplet.parseInt(0.5f*sqBar),11*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultDotBrightness_L)
     ;  
    cP5.addSlider("bkgSaturation")
     .setPosition(PApplet.parseInt(0.5f*sqBar),2*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultBkgSaturation)
     ;
    cP5.addSlider("dotSaturation_R")
     .setPosition(PApplet.parseInt(0.5f*sqBar),6*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultSaturation_R)
     ;  
    cP5.addSlider("dotSaturation_L")
     .setPosition(PApplet.parseInt(0.5f*sqBar),10*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultSaturation_L)
     ;  
    cP5.addSlider("dotSize")
     .setPosition(PApplet.parseInt(0.5f*sqBar),13*H)
     .setSize(200,28)
     .setRange(0,0.5f)
     .setNumberOfTickMarks(51)
     .setValue(dotSize)
     ;  
    cP5.addSlider("dotPosX")
     .setPosition(PApplet.parseInt(0.5f*sqBar),14*H)
     .setSize(200,28)
     .setRange(0,1)
     .setNumberOfTickMarks(51)
     .setValue(dotPosX)
     ;  
    cP5.addSlider("dotPosY")
     .setPosition(PApplet.parseInt(0.5f*sqBar),15*H)
     .setSize(200,28)
     .setRange(0,1)
     .setNumberOfTickMarks(51)
     .setValue(dotPosY)
     ;  
    cP5.addSlider("stimDelay")
     .setPosition(PApplet.parseInt(0.5f*sqBar),17*H)
     .setSize(200,28)
     .setRange(0,60)
     .setNumberOfTickMarks(61)
     .setValue(3)
     ;  
    cP5.addSlider("stimDuration")
     .setPosition(PApplet.parseInt(0.5f*sqBar),18*H)
     .setSize(200,28)
     .setRange(0,60)
     .setNumberOfTickMarks(61)
     .setValue(3)
     ;  
  cP5.addBang("Report_Settings",PApplet.parseInt(0.5f*sqBar),20*H,60,30);
  //cP5.addBang("Hide",sqBar-220,300,60,30);
  //cP5.addBang("Reverse",sqBar-220,350,60,30);
  cP5.addBang("Go",PApplet.parseInt(0.8f*sqBar),20*H,60,30);
  cP5.addBang("SETUP",PApplet.parseInt(0.8f*sqBar),22*H,60,30);
   
  stroke(0,0,0,0);

  String TIME = RTFN();
  logEntry(TIME + '\t' + "PROGRAM INITIATED", true);
}

public void keyPressed(){

  if (key == 'r'){Report_Settings();}
  else if (key == 'g'){Go();                }
  else {logEntry( "KEYSTROKE:" + str(key), true);}
  
}

public void SETUP(){
  SETUP = !SETUP;
}


public void Report_Settings(){
    logEntry("REPORT SETTINGS", true);
}



public void Go(){
  SETUP = false;
  RANDO = PApplet.parseInt(pow(-1, PApplet.parseInt(random(0,100))));
  t0 = millis();
  goNoGo = true;
  logEntry("START", true);
}



public void logEntry(String msg, boolean append) { 
  
  try {
    File file =new File("/sdcard/dotbot/log_binaryChoice.txt");
    if (!file.exists()) {
      file.createNewFile();
    }
 
    FileWriter fw = new FileWriter(file, append);///true = append
    BufferedWriter bw = new BufferedWriter(fw);
    PrintWriter pw = new PrintWriter(bw);
    if (NEWFILE == true){
      pw.write(HEADERS);
      println(HEADERS);
    }

    String defaultInfo = RTFN() 
                + '\t' + str(bkgColour)
                + '\t' + str(bkgBrightness)
                + '\t' + str(bkgSaturation)
                + '\t' + str(dotColour_R)
                + '\t' + str(dotBrightness_R)
                + '\t' + str(dotSaturation_R)
                + '\t' + str(dotColour_L)
                + '\t' + str(dotBrightness_L)
                + '\t' + str(dotSaturation_L)
                + '\t' + str(dotSize)
                + '\t' + str(dotPosX)
                + '\t' + str(dotPosY)
                + '\t' + str(RANDO) + '\t';
    pw.write(defaultInfo + msg + '\n');
    println(defaultInfo + msg + '\n');
    pw.close();
  }
  catch(IOException ioe) {
    System.out.println("Exception ");
    ioe.printStackTrace();
  }
}

public String RTFN(){
  Calendar cal = Calendar.getInstance(TimeZone.getTimeZone("GMT"));
  String foo;
  foo = formatter.format(cal.getTimeInMillis());
  return foo;
}


public void squareFrame(){
  fill(0,0,0,100);
  rect(0,0,sqBar, height);
  rect(width - sqBar,0,sqBar, height);
}


public void draw(){
  background(bkgColour,bkgSaturation,bkgBrightness,100);

  int dotSize_adj = PApplet.parseInt(dotSize*height);
  int dotPosX_adj = PApplet.parseInt(dotPosX*height);
  int dotPosY_adj = PApplet.parseInt(dotPosY*height);
  if (SETUP == true){
    fill(dotColour_L, dotSaturation_L, dotBrightness_L, 100);
    ellipse(width/2 - dotPosX_adj, dotPosY_adj, 1.4f*dotSize_adj, dotSize_adj);
    fill(dotColour_R, dotSaturation_R, dotBrightness_R, 100);
    ellipse(width/2 + dotPosX_adj, dotPosY_adj, 1.4f*dotSize_adj, dotSize_adj);
  }
    
  else if (goNoGo == true){
    
    if (tLoop - t0 >= stimDuration*1000 + stimDelay*1000){
      goNoGo = false;
      showDots = false;
      logEntry("STIM OFF",true);
    }
    else if (tLoop - t0 >= stimDelay*1000){
      if (showDots == false){
        logEntry("STIM ON", true);
        showDots = true;
      }
      fill(dotColour_L, dotSaturation_L, dotBrightness_L, 100);
      ellipse(width/2 - RANDO*dotPosX_adj, dotPosY_adj, 1.4f*dotSize_adj, dotSize_adj);
      fill(dotColour_R, dotSaturation_R, dotBrightness_R, 100);
      ellipse(width/2 + RANDO*dotPosX_adj, dotPosY_adj, 1.4f*dotSize_adj, dotSize_adj);
    }
    tLoop = millis();

  }
  squareFrame();
}
  public void settings() {  fullScreen(); }
}
