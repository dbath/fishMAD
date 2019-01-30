

//-------------------------- DO NOT CHANGE VALUES ABOVE------------------------------------


float stimDelay = 1.0; //delay between pressing "go" and presentation of stimulus
float stimDuration = 10.0; //duration of stimulus presentation in seconds 

int dotSize = 250;  // size of dots in pixels
int dotX = 550; //horizontal distance of dots from centre, in pixels

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

int bkgColour;
int dotColour_R;
int dotColour_L;
int bkgBrightness;
int dotBrightness_R;
int dotBrightness_L;
int bkgSaturation;
int dotSaturation_R;
int dotSaturation_L;


void setup(){

  
  
  colorMode(HSB, 100,100,100,100);
  fullScreen();
  ellipseMode(CENTER);
  sqBar = (width - height) /2;
  
  cP5 = new ControlP5(this);
  
  cP5.addSlider("bkgColour")
     .setPosition(sqBar-300,50+0*40)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultBkgColour)
     ;
    cP5.addSlider("dotColour_R")
     .setPosition(sqBar-300,50+4*40)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultDotColour_R)
     ;  
    cP5.addSlider("dotColour_L")
     .setPosition(sqBar-300,50+8*40)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultDotColour_L)
     ;  
    cP5.addSlider("bkgBrightness")
     .setPosition(sqBar-300,50+2*40)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultBkgBrightness)
     ;
    cP5.addSlider("dotBrightness_R")
     .setPosition(sqBar-300,50+6*40)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultDotBrightness_R)
     ;  
    cP5.addSlider("dotBrightness_L")
     .setPosition(sqBar-300,50+10*40)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultDotBrightness_L)
     ;  
    cP5.addSlider("bkgSaturation")
     .setPosition(sqBar-300,50+1*40)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultBkgSaturation)
     ;
    cP5.addSlider("dotSaturation_R")
     .setPosition(sqBar-300,50+5*40)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultSaturation_R)
     ;  
    cP5.addSlider("dotSaturation_L")
     .setPosition(sqBar-300,50+9*40)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultSaturation_L)
     ;  
  cP5.addBang("Report_Settings",sqBar-300,50+12*40,60,30);
  //cP5.addBang("Hide",sqBar-220,300,60,30);
  //cP5.addBang("Reverse",sqBar-220,350,60,30);
  cP5.addBang("Go",sqBar-130,50+12*40,60,30);
  cP5.addBang("SETUP",sqBar-220,50+15*40,60,30);
   
  stroke(0,0,0,0);

  String TIME = RTFN();
  logEntry(TIME + '\t' + "PROGRAM INITIATED", true);
  logEntry(TIME + '\t' + "BKGCOLOUR" 
                + '\t' + "BKGBRIGHTNESS"
                + '\t' + "BKGSAT" 
                + '\t' + "DOTCOLOUR_R" 
                + '\t' + "DOTBRIGHTNESS_R" 
                + '\t' + "DOTSAT_R" 
                + '\t' + "DOTCOLOUR_L" 
                + '\t' + "DOTBRIGHTNESS_L" 
                + '\t' + "DOTSAT_R" 
                + '\t' + "COMMENT" + '\n', true);
}

void keyPressed(){

  if (key == 'r'){Report_Settings();}
  else if (key == 'g'){Go();
    logEntry(RTFN() + '\t' + bkgColour
                    + '\t' + bkgBrightness
                    + '\t' + bkgSaturation
                    + '\t' + dotColour_R
                    + '\t' + dotBrightness_R
                    + '\t' + dotSaturation_R
                    + '\t' + dotColour_L
                    + '\t' + dotBrightness_L
                    + '\t' + dotSaturation_L
                    + '\t' + "EXPERIMENT START" + '\n', true);
                }

  else {
    logEntry(RTFN() + '\t' + bkgColour
                    + '\t' + bkgBrightness
                    + '\t' + bkgSaturation
                    + '\t' + dotColour_R
                    + '\t' + dotBrightness_R
                    + '\t' + dotSaturation_R
                    + '\t' + dotColour_L
                    + '\t' + dotBrightness_L
                    + '\t' + dotSaturation_L
                  + '\t' + "KEYSTROKE:" + str(key) + '\n', true);
  }
  
}

void SETUP(){
  SETUP = !SETUP;
}


void Report_Settings(){
    logEntry(RTFN() + '\t' + bkgColour
                    + '\t' + bkgBrightness
                    + '\t' + bkgSaturation
                    + '\t' + dotColour_R
                    + '\t' + dotBrightness_R
                    + '\t' + dotSaturation_R
                    + '\t' + dotColour_L
                    + '\t' + dotBrightness_L
                    + '\t' + dotSaturation_L
                  + '\t' + "REPORT SETTINGS" + '\n', true);
}



void Go(){
  goNoGo = true;
  t0 = millis();
}



void logEntry(String msg, boolean append) { 
  try {
    File file =new File("/sdcard/dotbot/log_binaryChoice.txt");
    if (!file.exists()) {
      file.createNewFile();
    }
 
    FileWriter fw = new FileWriter(file, append);///true = append
    BufferedWriter bw = new BufferedWriter(fw);
    PrintWriter pw = new PrintWriter(bw);

    pw.write(msg);
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

  if (SETUP == true){
    fill(dotColour_L, dotSaturation_L, dotBrightness_L, 100);
    ellipse(width/2 - dotX, height/2, dotSize, dotSize);
    fill(dotColour_R, dotSaturation_R, dotBrightness_R, 100);
    ellipse(width/2 + dotX, height/2, dotSize, dotSize);
  }
    
  else if (goNoGo == true){
    
    if (tLoop - t0 >= stimDuration*1000 + stimDelay*1000){
      goNoGo = false;
    }
    else if (tLoop - t0 >= stimDelay*1000){
      fill(dotColour_L, dotSaturation_L, dotBrightness_L, 100);
      ellipse(width/2 - dotX, height/2, dotSize*1.8, dotSize);
      fill(dotColour_R, dotSaturation_R, dotBrightness_R, 100);
      ellipse(width/2 + dotX, height/2, dotSize*1.8, dotSize);
    }
    tLoop = millis();

  }
  squareFrame();
}
