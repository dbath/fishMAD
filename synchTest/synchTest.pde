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


//Logging setup
FileWriter fw;
BufferedWriter bw;
DecimalFormat formatter = new DecimalFormat("###.#");

int sqBar;
int screenSize = displayHeight;
int t0;

void setup(){
  colorMode(HSB, 100,100,100,100);
  stroke(0,0,0,0);
  fill(0,0,0,100);
  //size(displayHeight, displayHeight);
  
  fullScreen();
  ellipseMode(CENTER);
  sqBar = (width - height) /2;
  t0 = millis();

  logEntry("start\t" + RTFN() + '\n', false);



}

void draw(){

  background(0,0,100,100);
  stroke(0,0,0,100);
  fill(0,0,0,100);
  textSize(55);
  text("Current time:", width*.30, height*.35);
  String time = RTFN();
  text(time, width*0.5, height*0.5);  
  
  if (millis() - t0 > 3000){
    t0 = millis();
    logEntry("Blip\t" + time + '\n', true);
    ellipse(width*0.7, height*0.25, 250, 250);
  }
    
  
  
  
  squareFrame();
}

void squareFrame(){
  fill(0,0,0,100);
  rect(0,0,sqBar, height);
  rect(width - sqBar,0,sqBar, height);
}

void logEntry(String msg, boolean newfile) { 
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

public String RTFN(){
  Calendar cal = Calendar.getInstance(TimeZone.getTimeZone("GMT"));
  String foo;
  foo = formatter.format(cal.getTimeInMillis());
  return foo;
}