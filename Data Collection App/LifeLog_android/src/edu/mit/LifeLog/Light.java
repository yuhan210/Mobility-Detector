package edu.mit.LifeLog;

//import java.text.SimpleDateFormat;
//import java.util.Calendar;
import java.util.List;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;

public class Light implements edu.mit.LifeLog.Sensor
{
	private Context context;
	
	private SensorManager sensorManager;
	private Sensor lightSensor;
	private SensorEventListener proximitySensorListener;
	
	private String debugStatus;
	private boolean isEnabled;
	// either one of SENSOR_DELAY_UI, SENSOR_DELAY_GAME, SENSOR_DELAY_FASTEST, SENSOR_DELAY_NORMAL
	private int scanFrequency;
	private Logger logger;
	private SensorType type;
	
	public Light(Context ctx, Logger logger)
	{
		this.context = ctx;
		this.logger = logger;
		
		this.sensorManager = (SensorManager)context.getSystemService(Context.SENSOR_SERVICE);
		this.proximitySensorListener = new ProximityListener();
		List<Sensor> sensors = sensorManager.getSensorList(Sensor.TYPE_LIGHT);	
        this.lightSensor = (sensors.size() > 0) ? sensors.get(0) : null;
        this.isEnabled = false;
        this.scanFrequency = 0;
        this.type = SensorType.Light;
        this.debugStatus = "no status";
        
        // default setting
        changeSettings(type + FieldDelimiter + "1" + FieldDelimiter + SensorManager.SENSOR_DELAY_FASTEST);
	}	
	
	@Override
	public SensorType getType() 
	{
		return type;
	}

	@Override
	public void changeSettings(String settings) 
	{
		String [] splitted = settings.split(FieldDelimiter);
		if (splitted.length != 3 || !splitted[0].equals(type.toString()))			
			throw new RuntimeException("wrong setting string for light: " + settings);
		
		// no accelerometer available
		if (lightSensor == null) return;
		
		// cancel the current scanning 
		sensorManager.unregisterListener(proximitySensorListener);
		
		this.isEnabled = (splitted[1].equals("1"));
		this.scanFrequency = Integer.parseInt(splitted[2]);
		System.out.println("change Light settings to: (" + isEnabled + ", " + scanFrequency + ")");
		if (isEnabled)		
			sensorManager.registerListener(proximitySensorListener, lightSensor, scanFrequency);
		else 
			logger.flushFile(type);
	}

	@Override
	public String getSettingsString() 
	{
		if (isEnabled)
			return type + FieldDelimiter + "1" + FieldDelimiter + scanFrequency;
		else
			return type + FieldDelimiter + "0" + FieldDelimiter + scanFrequency;
	}

	@Override
	public void stop()
	{
		sensorManager.unregisterListener(proximitySensorListener);
		logger.flushFile(type);
	}
	
	@Override
	public String getDebugStatus() 
	{
		return type + FieldDelimiter + debugStatus;
	}
	
	static int num = 0;
	
	private class ProximityListener implements SensorEventListener 
    {
    	public void onSensorChanged(SensorEvent event)
        {    		
    		System.out.println("light sensor data received");
    		/*
    		float x = event.values[SensorManager.DATA_X];
    		float y = event.values[SensorManager.DATA_Y];
    		float z = event.values[SensorManager.DATA_Z];
    		    	
    		String record = x + PayloadFieldDelimiter + y + PayloadFieldDelimiter + z;
    		*/
    		String record = "" + event.values[0];
    		// debug
    		//record += " " + num + " " +  LifeLogService.getReadableCurrentTime();
    		++num;

    		String timestamp = System.currentTimeMillis() + "";
    		logger.writeRecord(type, timestamp, record);
    		debugStatus = LifeLogService.getReadableCurrentTime();
    		System.out.println("light sensor data: " + record + " timestamp: " + timestamp);
        }
    	
        public void onAccuracyChanged(Sensor sensor, int accuracy) {}
    }
}
