package edu.mit.LifeLog;

import java.util.Timer;
import java.util.TimerTask;

import android.content.Context;
import android.view.MotionEvent;

public class TouchScreen implements edu.mit.LifeLog.Sensor{
	private Context context;
	private Logger logger;
	private boolean isEnabled;
	private int scanIntervalInMs;
	private SensorType type;
	private String debugStatus;
	private static int curGroundTruth;
	private Timer timer;
	private boolean isTouching;
	
	public TouchScreen(Context ctx, Logger logger){
		this.context = ctx;
		this.logger = logger;
		this.isEnabled = false;
		this.scanIntervalInMs = 0;
		//this.type = SensorType.TouchScreen;
		this.debugStatus = "no status";	
		this.timer = new Timer();
		this.isTouching = false;
		
		curGroundTruth = 0;
	    // default setting
        changeSettings(type + FieldDelimiter + "1" + FieldDelimiter + "1000");

	}
	public static void setGroundTruth(int gt){
		   curGroundTruth = gt;
	}
	@Override
	public SensorType getType() {
		return type;
	}

	@Override
	public void changeSettings(String settings) {
		String [] splitted = settings.split(FieldDelimiter);
		if (splitted.length != 3 || !splitted[0].equals(type.toString()))			
			throw new RuntimeException("wrong setting string for touch screen: " + settings + " len: " + splitted.length + " 0: " + splitted[0]);
		
		// cancel the current scanning 
		timer.cancel();
		
		this.isEnabled = (splitted[1].equals("1"));
		this.scanIntervalInMs = Integer.parseInt(splitted[2]);
		System.out.println("change touch screen settings to: (" + isEnabled + ", " + scanIntervalInMs + ")");
		if (isEnabled)
		{
			this.timer = new Timer();
			TimerTask ts = new TimerTask() { public void run() { writeLog(); } };					
		
			timer.schedule(ts, 0, scanIntervalInMs);
			}
		else
			logger.flushFile(type);
	}
	public boolean onTouchEvent (MotionEvent event){
		
		int ev = event.getAction();
		switch(ev){
			case MotionEvent.ACTION_DOWN:
				setIsTouching(true);
				break;
			case MotionEvent.ACTION_MOVE:
				setIsTouching(true);
				break;
			case MotionEvent.ACTION_UP:
				setIsTouching(false);
				break;
			case MotionEvent.ACTION_CANCEL:
				setIsTouching(false);
				break;
				
		}
		
		return true;
	}
	public void setIsTouching(boolean b){
		this.isTouching = b;
	}
	
	public void writeLog(){

		String record = "";
		if(isTouching)
			record += PayloadFieldDelimiter + curGroundTruth + PayloadFieldDelimiter + "1";
		else
			record += PayloadFieldDelimiter + curGroundTruth + PayloadFieldDelimiter + "0";;
		logger.writeRecord(type, System.currentTimeMillis() + "", record);
		System.out.println(record);
		debugStatus = LifeLogService.getReadableCurrentTime(); //scanResults.size() + "";

	}
	@Override
	public String getSettingsString() {
		if (isEnabled)
			return type + FieldDelimiter + "1" + FieldDelimiter + scanIntervalInMs;
		else
			return type + FieldDelimiter + "0" + FieldDelimiter + scanIntervalInMs;
	
	}

	@Override
	public void stop() {
		if (isEnabled)
			
		timer.cancel();
		logger.flushFile(type);	
	}

	@Override
	public String getDebugStatus() {
		return getType() + FieldDelimiter + debugStatus;

	}

}
