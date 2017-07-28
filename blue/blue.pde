import java.io.FileWriter;
import java.io.*;
import java.util.*;
import java.math.BigDecimal;
import java.text.DecimalFormat;
import java.time.Instant;
import java.sql.Timestamp;
import java.util.Collections;


//Logging setup
FileWriter fw;
BufferedWriter bw;
DecimalFormat formatter = new DecimalFormat("###.#");
Calendar cal = Calendar.getInstance(TimeZone.getTimeZone("GMT"));

//Drawing variables
int sqBar; 


void setup(){
  
  colorMode(HSB, 100,100,100,100);
  stroke(0,0,0,0);
  fill(60,100,65,100);
  //size(displayHeight, displayHeight);
  
  fullScreen();
  ellipseMode(CENTER);
  sqBar = (width - height) /2;


  background(55,100,100,100);
  squareFrame();
  println(RTFN() + "\tResting Blue started \n");
  logEntry(RTFN() + "\tResting Blue started \n");



}

void draw(){
  
  
}

void stop() {
  println(RTFN() + "\t Resting Blue stopped \n");
  logEntry(RTFN() + "\t Resting Blue stopped.\n");
}


void logEntry(String msg) { 
  try {
    File file =new File("/sdcard/dan_Data/dotbot_stimlog.txt");
    if (!file.exists()) {
      file.createNewFile();
    }
 
    FileWriter fw = new FileWriter(file, true);///true = append
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
  String foo;
  foo = formatter.format(cal.getTimeInMillis());
  return foo;
}

void squareFrame(){
  fill(0,0,0,100);
  rect(0,0,sqBar, height);
  rect(width - sqBar,0,sqBar, height);
}