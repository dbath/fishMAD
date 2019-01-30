




//-------------------------- DO NOT CHANGE VALUES ABOVE------------------------------------


float stimDelay = 3.0; //delay between pressing "go" and presentation of stimulus
float stimDuration = 3.0; //duration of stimulus presentation in seconds 

float dotSize = 0.1;  // size of dots in proportion of screen height (eg 0.5 will be half the height of the screen)
float dotPosX = 0.4; //horizontal distance of dots from centre, in proportion of screen height
float dotPosY = 0.5; //vertical distance of dots from top, in proportion of screen height

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


import java.io.FileWriter;
import java.io.*;
import java.util.*;
import java.math.BigDecimal;
import java.text.DecimalFormat;
import java.time.Instant;
import java.sql.Timestamp;
import java.util.Collections;


//GUI Setup



import controlP5.*;
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
float stopgo = 1.0;
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
boolean NEWFILE = false;
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

void setup(){

  
  println(str(height) + '\t' + str(width));
  colorMode(HSB, 100,100,100,100);
  fullScreen();
  ellipseMode(CENTER);
  
  //adjust sizing relative to screen size:
  
  sqBar = (width - height) /2;
  
  int H = int(0.03*height);
  
  // setup GUI
  
  
  cP5 = new ControlP5(this);
  
  
  cP5.addSlider("bkgColour")
     .setPosition(int(0.1*sqBar),1*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultBkgColour)
     ;
    cP5.addSlider("dotColour_R")
     .setPosition(int(0.1*sqBar),5*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultDotColour_R)
     ;  
    cP5.addSlider("dotColour_L")
     .setPosition(int(0.1*sqBar),9*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultDotColour_L)
     ;  
    cP5.addSlider("bkgBrightness")
     .setPosition(int(0.1*sqBar),3*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultBkgBrightness)
     ;
    cP5.addSlider("dotBrightness_R")
     .setPosition(int(0.1*sqBar),7*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultDotBrightness_R)
     ;  
    cP5.addSlider("dotBrightness_L")
     .setPosition(int(0.1*sqBar),11*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultDotBrightness_L)
     ;  
    cP5.addSlider("bkgSaturation")
     .setPosition(int(0.1*sqBar),2*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultBkgSaturation)
     ;
    cP5.addSlider("dotSaturation_R")
     .setPosition(int(0.1*sqBar),6*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultSaturation_R)
     ;  
    cP5.addSlider("dotSaturation_L")
     .setPosition(int(0.1*sqBar),10*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultSaturation_L)
     ;  
    cP5.addSlider("dotSize")
     .setPosition(int(0.1*sqBar),13*H)
     .setSize(200,28)
     .setRange(0,0.5)
     .setNumberOfTickMarks(51)
     .setValue(dotSize)
     ;  
    cP5.addSlider("dotPosX")
     .setPosition(int(0.1*sqBar),14*H)
     .setSize(200,28)
     .setRange(0,1)
     .setNumberOfTickMarks(51)
     .setValue(dotPosX)
     ;  
    cP5.addSlider("dotPosY")
     .setPosition(int(0.1*sqBar),15*H)
     .setSize(200,28)
     .setRange(0,1)
     .setNumberOfTickMarks(51)
     .setValue(dotPosY)
     ;  
    cP5.addSlider("stimDelay")
     .setPosition(int(0.1*sqBar),17*H)
     .setSize(200,28)
     .setRange(0,60)
     .setNumberOfTickMarks(61)
     .setValue(3)
     ;  
    cP5.addSlider("stimDuration")
     .setPosition(int(0.1*sqBar),18*H)
     .setSize(200,28)
     .setRange(0,60)
     .setNumberOfTickMarks(61)
     .setValue(3)
     ;  
    cP5.addBang("Report_Settings",int(0.1*sqBar),20*H,60,30);
    //cP5.addBang("Hide",sqBar-220,300,60,30);
    //cP5.addBang("Reverse",sqBar-220,350,60,30);
    cP5.addBang("Go",int(0.5*sqBar),20*H,60,30);
    cP5.addToggle("SETUP")
     .setPosition(int(0.5*sqBar),22*H)
     .setSize(60,30);
   
  stroke(0,0,0,0);

  logEntry("PROGRAM INITIATED", true);
}

void keyPressed(){

  if (key == 'r'){Report_Settings();}
  else if (key == 'g'){Go();                }
  else {logEntry( "KEYSTROKE:" + str(key), true);}
  
}

void SETUP(){
  SETUP = !SETUP;
}


void Report_Settings(){
    logEntry("REPORT SETTINGS", true);
}



void Go(){
  SETUP = false;
  RANDO = int(pow(-1, int(random(0,100))));
  t0 = millis();
  goNoGo = true;
  logEntry("START", true);
}



void logEntry(String msg, boolean append) { 
  
  try {
    File file =new File("/sdcard/dotbot/log_binaryChoice.txt");
    if (!file.exists()) {
      file.createNewFile();
      NEWFILE = true;
    }
 
    FileWriter fw = new FileWriter(file, append);///true = append
    BufferedWriter bw = new BufferedWriter(fw);
    PrintWriter pw = new PrintWriter(bw);
    if (NEWFILE == true){
      pw.write(HEADERS);
      println(HEADERS);
      NEWFILE = false;
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


void squareFrame(){
  fill(0,0,0,100);
  rect(0,0,sqBar, height);
  rect(width - sqBar,0,sqBar, height);
}


void draw(){
  background(bkgColour,bkgSaturation,bkgBrightness,100);

  int dotSize_adj = int(dotSize*height);
  int dotPosX_adj = int(dotPosX*height);
  int dotPosY_adj = int(dotPosY*height);
  if (SETUP == true){
    fill(dotColour_L, dotSaturation_L, dotBrightness_L, 100);
    ellipse(width/2 - dotPosX_adj, dotPosY_adj, 1.4*dotSize_adj, dotSize_adj);
    fill(dotColour_R, dotSaturation_R, dotBrightness_R, 100);
    ellipse(width/2 + dotPosX_adj, dotPosY_adj, 1.4*dotSize_adj, dotSize_adj);
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
      ellipse(width/2 - RANDO*dotPosX_adj, dotPosY_adj, 1.4*dotSize_adj, dotSize_adj);
      fill(dotColour_R, dotSaturation_R, dotBrightness_R, 100);
      ellipse(width/2 + RANDO*dotPosX_adj, dotPosY_adj, 1.4*dotSize_adj, dotSize_adj);
    }
    tLoop = millis();

  }
  squareFrame();
}
