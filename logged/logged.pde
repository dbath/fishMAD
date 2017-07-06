import java.io.FileWriter;
import java.io.*;
import java.util.*;
import java.math.BigDecimal;
import java.text.DecimalFormat;
import java.time.Instant;
import java.sql.Timestamp;

FileWriter fw;
BufferedWriter bw;


//Date d = new Date();
DecimalFormat formatter = new DecimalFormat("###.#");

int sqBar;

void setup(){
  
  //requestPermission("android.permission.WRITE_EXTERNAL_STORAGE");
  
  colorMode(HSB, 100,100,100,100);
  fullScreen();
  ellipseMode(CENTER);
  sqBar = (width - height) /2;
  background(0,0,00,100);
  stroke(0,0,0,0);
  fill(55,100,100,100);
  rect(sqBar , 0, height, height); 
  //println("--------------------------look down-------------------");
  //print(str(cw.fileList()[0]));
  //logIt("hello world!");
  //println("--------------------------look up-------------------");
}




void logIt(String msg) { 
  try {
    File file =new File("/sdcard/dan_Data/dotbot_log.txt");
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
  foo = formatter.format(System.currentTimeMillis());
  return foo;
}

void draw(){
  
  logIt("hello world!\t" + RTFN() + '\n');
  delay(1000);
  print(RTFN());
}

 
 
 