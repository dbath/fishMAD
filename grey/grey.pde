import java.io.FileWriter;
import java.io.*;
import java.util.*;
import java.math.BigDecimal;
import java.text.DecimalFormat;
import java.time.Instant;
import java.sql.Timestamp;
import java.util.Collections;
import java.nio.*;
import java.net.*;

import controlP5.*;
ControlP5 cP5;
Slider abc;

//Logging setup
FileWriter fw;
BufferedWriter bw;
DecimalFormat formatter = new DecimalFormat("###.#");

int sqBar;
int screenSize = displayHeight;
int brightVal;
boolean dispVal;

void setup(){
  colorMode(HSB, 100,100,100,100);
  stroke(0,0,0,0);
  fill(0,0,0,100);
  
  fullScreen();
  ellipseMode(CENTER);
  sqBar = (width - height) /2;
  cP5 = new ControlP5(this);
  
  cP5.addSlider("brightVal")
     .setPosition(120,90)
     .setSize(200,28)
     .setRange(0,100)
     .setNumberOfTickMarks(1001)
     .setValue(50)
     ;

}

void draw(){

  background(0,0,brightVal,100);
  stroke(0,0,0,100);
  fill(0,0,0,100);
  squareFrame();
  showText();
}

void keyPressed(){
  if (key == CODED) {
    if (keyCode == UP) {
      brightVal = brightVal +2;
    } 
    else if (keyCode == DOWN) {
      brightVal = brightVal -2;
    }
  }
  if (key == 'b'){   ///BLACK
    brightVal = 0;
  }
  if (key == 'w'){  //WHITE
    brightVal = 100;
  }
  if (key == 'd'){   ///DISPLAY VALUE
    dispVal = !dispVal;
  }
  cP5.getController("brightVal").setValue(brightVal);  
  
}




void squareFrame(){
  fill(0,0,0,100);
  rect(0,0,sqBar, height);
  rect(width - sqBar,0,sqBar, height);
}

void logEntry(String msg, boolean newfile) { 
  // msg: pass the message you want to send,
  // newfile: make true if you want to append to the existing file. false to overwrite any existing file with that name.
  try {
    File file =new File("/sdcard/dan_Data/synchTest_log.txt");
    if (!file.exists()) {
      file.createNewFile();
    }
 
    FileWriter fw = new FileWriter(file, newfile);///true = append
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

void showText(){
  stroke(0,100,100,100);
  fill(0,100,100,100);
  if (dispVal == true){
    textSize(200);
    text(str(brightVal), width*.60, height*.75);  
  }
 
}

public String RTFN(){
  Calendar cal = Calendar.getInstance(TimeZone.getTimeZone("GMT"));
  String foo;
  foo = formatter.format(cal.getTimeInMillis());
  return foo;
}