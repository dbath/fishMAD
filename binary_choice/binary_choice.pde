




//-------------------------- DO NOT CHANGE VALUES ABOVE------------------------------------


float stimDelay = 3.0; //delay between pressing "go" and presentation of stimulus
float stimDuration = 3.0; //duration of stimulus presentation in seconds 

float dotSize = 0.01;  // size of dots in proportion of screen height (eg 0.5 will be half the height of the screen)
float dotPosX = 0.33; //horizontal distance of dots from centre, in proportion of screen height
float dotPosY = 0.5; //vertical distance of dots from top, in proportion of screen height

int defaultBkgColour = 50; //default colour of background from 0 (red) to 100 (red) ROYGBIVR
int defaultBkgBrightness = 100; //default brightness of background from 0 (black) to 100 (white)
int defaultBkgSaturation = 50; //default colour of background from 0 (black) to 100 (white)

int defaultdotColour_1 = 44; //default colour of dots from 0 (red) to 100 (red) ROYGBIVR
int defaultDotBrightness_1 = 100; //default colour of dots from 0 (black) to 100 (bright)
int defaultSaturation_1 = 64; //default colour of dots from 0 (black) to 100 (white)

int defaultdotColour_2 = 50; //default colour of dots from 0 (red) to 100 (red) ROYGBIVR
int defaultDotBrightness_2 = 100; //default colour of dots from 0 (black) to 100 (white)
int defaultSaturation_2 = 50; //default colour of dots from 0 (black) to 100 (white)


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
boolean HIDE = false;
//Logging setup
FileWriter fw;
BufferedWriter bw;
DecimalFormat formatter = new DecimalFormat("###.#");

int H;
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
int dotColour_1;
int dotColour_2;
int bkgBrightness;
int dotBrightness_1;
int dotBrightness_2;
int bkgSaturation;
int dotSaturation_1;
int dotSaturation_2;
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
  
  H = int(0.03*height);
  
  // setup GUI
  
  
  cP5 = new ControlP5(this);
  
  
  cP5.addSlider("bkgColour")
     .setPosition(int(0.1*sqBar),1*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultBkgColour)
     ;
    cP5.addSlider("dotColour_1")
     .setPosition(int(0.1*sqBar),5*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultdotColour_1)
     ;  
    cP5.addSlider("dotColour_2")
     .setPosition(int(0.1*sqBar),9*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultdotColour_2)
     ;  
    cP5.addSlider("bkgBrightness")
     .setPosition(int(0.1*sqBar),3*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultBkgBrightness)
     ;
    cP5.addSlider("dotBrightness_1")
     .setPosition(int(0.1*sqBar),7*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultDotBrightness_1)
     ;  
    cP5.addSlider("dotBrightness_2")
     .setPosition(int(0.1*sqBar),11*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultDotBrightness_2)
     ;  
    cP5.addSlider("bkgSaturation")
     .setPosition(int(0.1*sqBar),2*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultBkgSaturation)
     ;
    cP5.addSlider("dotSaturation_1")
     .setPosition(int(0.1*sqBar),6*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultSaturation_1)
     ;  
    cP5.addSlider("dotSaturation_2")
     .setPosition(int(0.1*sqBar),10*H)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(51)
     .setValue(defaultSaturation_2)
     ;  
    cP5.addSlider("dotSize")
     .setPosition(int(0.1*sqBar),13*H)
     .setSize(200,28)
     .setRange(0,0.1)
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
    cP5.addToggle("HIDE")
     .setPosition(int(0.1*sqBar),22*H)
     .setSize(60,30);
    cP5.addToggle("SETUP")
     .setPosition(int(0.5*sqBar),22*H)
     .setSize(60,30);
   
  //stroke(0,0,0,0);

  logEntry("PROGRAM INITIATED", true);
}

void keyPressed(){

  if (key == 'r'){Report_Settings();}
  else if (key == 'g'){Go();                }
  else if (key == 's'){SETUP();                }
  else {logEntry( "KEYSTROKE:" + str(key), true);}
  
}

void SETUP(){
  SETUP = !SETUP;
}

void HIDE(){
  HIDE = !HIDE;
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
                + '\t' + str(dotColour_1)
                + '\t' + str(dotBrightness_1)
                + '\t' + str(dotSaturation_1)
                + '\t' + str(dotColour_2)
                + '\t' + str(dotBrightness_2)
                + '\t' + str(dotSaturation_2)
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
  if (HIDE == true){ background(0,0,100,100);}
  else {
    background(bkgColour,bkgSaturation,bkgBrightness,100);
  
    int dotSize_adj = int(dotSize*height);
    int dotPosX_adj = int(dotPosX*height);
    int dotPosY_adj = int(dotPosY*height);
    if (SETUP == true){
      stroke(dotColour_2, dotSaturation_2, dotBrightness_2, 100);
      fill(dotColour_2, dotSaturation_2, dotBrightness_2, 100);
      ellipse(width/2 - dotPosX_adj, dotPosY_adj, 1.4*dotSize_adj, dotSize_adj);
      fill(dotColour_1, dotSaturation_1, dotBrightness_1, 100);
      stroke(dotColour_1, dotSaturation_1, dotBrightness_1, 100);
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
        stroke(dotColour_2, dotSaturation_2, dotBrightness_2, 100);
        fill(dotColour_2, dotSaturation_2, dotBrightness_2, 100);
        ellipse(width/2 - RANDO*dotPosX_adj, dotPosY_adj, 1.4*dotSize_adj, dotSize_adj);
        stroke(dotColour_1, dotSaturation_1, dotBrightness_1, 100);
        fill(dotColour_1, dotSaturation_1, dotBrightness_1, 100);
        ellipse(width/2 + RANDO*dotPosX_adj, dotPosY_adj, 1.4*dotSize_adj, dotSize_adj);
      }
      tLoop = millis();
  
    }
  }
  stroke(0,0,0,0);
  squareFrame();
  fill(0,0,100,100);
  textSize(40);
  if (RANDO == 1){  text("Cue 1 is right", int(0.2*sqBar),28*H);}
  else if (RANDO == -1){  text("Cue 1 is left", int(0.2*sqBar),28*H);}
}
