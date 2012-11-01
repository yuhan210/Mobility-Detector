package edu.mit.LifeLog;

import java.util.List;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import edu.mit.LifeLog.Sensor.SensorType;

public class GYRO implements edu.mit.LifeLog.Sensor{
private Context context;
	
	private SensorManager sensorManager;
	private Sensor gyroscope;
	private SensorEventListener gyroSensorListener;
	
	private String debugStatus;
	private boolean isEnabled;
	// either one of SENSOR_DELAY_UI, SENSOR_DELAY_GAME, SENSOR_DELAY_FASTEST, SENSOR_DELAY_NORMAL
	private int scanFrequency;
	private Logger logger;
	private SensorType type;
	private static int curGroundTruth;
	
	public GYRO(Context ctx, Logger logger){
		this.context = ctx;
		this.logger = logger;
		
		this.sensorManager = (SensorManager)context.getSystemService(Context.SENSOR_SERVICE);
		this.gyroSensorListener = new GyroListener();
		List<Sensor> sensors = sensorManager.getSensorList(Sensor.TYPE_GYROSCOPE);	
        this.gyroscope = (sensors.size() > 0) ? sensors.get(0) : null;
        this.isEnabled = false;
        this.scanFrequency = 0;
        this.type = SensorType.GYRO;
        this.debugStatus = "no status";
       
        
        // default setting
        changeSettings(type + FieldDelimiter + "1" + FieldDelimiter + SensorManager.SENSOR_DELAY_FASTEST);

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
		if (splitted.length !=3 || !splitted[0].equals(type.toString()))			
			throw new RuntimeException("wrong setting string for gyro: " + settings);
		
		// no gyro available
		if (gyroscope == null) return;
		
		// cancel the current scanning 
		sensorManager.unregisterListener(gyroSensorListener);
		
		this.isEnabled = (splitted[1].equals("1"));
		this.scanFrequency = Integer.parseInt(splitted[2]);
		System.out.println("change gyro settings to: (" + isEnabled + ", " + scanFrequency + ")");
		if (isEnabled)	
			sensorManager.registerListener(gyroSensorListener, gyroscope, scanFrequency);
		else 
			logger.flushFile(type);

	}
	@Override
	public String getSettingsString() {
		if (isEnabled)
			return type + FieldDelimiter + "1" + FieldDelimiter + scanFrequency;
		else
			return type + FieldDelimiter + "0" + FieldDelimiter + scanFrequency;
	}
	@Override
	public void stop() {
		sensorManager.unregisterListener(gyroSensorListener);
		logger.flushFile(type);
			
	}
	@Override
	public String getDebugStatus() {
		return type + FieldDelimiter + debugStatus;

	}
	
	private class GyroListener implements SensorEventListener 
    {
    	public void onSensorChanged(SensorEvent event)
        {    		
    		System.out.println("gyro data received");
    		float x = event.values[SensorManager.DATA_X];
    		float y = event.values[SensorManager.DATA_Y];
    		float z = event.values[SensorManager.DATA_Z];
    		    	
    		String record = x + PayloadFieldDelimiter + y + PayloadFieldDelimiter + z + PayloadFieldDelimiter + curGroundTruth;
    		// debug
    		//record += " " + num + " " +  LifeLogService.getReadableCurrentTime();
    		//++num;

    		String timestamp = System.currentTimeMillis() + "";
    		logger.writeRecord(type, timestamp, record);
    		debugStatus = LifeLogService.getReadableCurrentTime();
        }
    	
        public void onAccuracyChanged(Sensor sensor, int accuracy) {}
    }
	
}
