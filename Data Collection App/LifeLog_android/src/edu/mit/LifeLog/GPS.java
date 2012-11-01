package edu.mit.LifeLog;

import android.content.Context;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;

public class GPS implements Sensor
{
	private LocationManager locationManager;
    private LocationListener locationListener;
	private Context context;
	private Logger logger;
	private SensorType type;
	private boolean isEnabled;
	private int scanIntervalInMs;
	private static int curGroundTruth;
	
	private int gpsStatusCode = 0;
	
	private String debugStatus = "";

	public GPS(Context ctx, Logger logger)
	{
		this.context = ctx;
		this.logger = logger;
		this.type = SensorType.GPS;
		this.isEnabled = false;
		this.locationManager = (LocationManager)context.getSystemService(Context.LOCATION_SERVICE);
		this.locationListener = new GPSLocationListener();		
		this.scanIntervalInMs = 0;		
		this.debugStatus = "no status";	
		
        // default setting
        changeSettings(type + FieldDelimiter + "1" + FieldDelimiter + "1000");
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
			throw new RuntimeException("wrong setting string for gps: " + settings);
		
		// cancel the current scanning 
		locationManager.removeUpdates(locationListener);
		
		this.isEnabled = (splitted[1].equals("1"));
		this.scanIntervalInMs = Integer.parseInt(splitted[2]);
		System.out.println("change GPS settings to: (" + isEnabled + ", " + scanIntervalInMs + ")");
		if (isEnabled)		
			locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, scanIntervalInMs, 0, locationListener);
		else
			logger.flushFile(type);
	}
	public static void setGroundTruth(int gt){
		   curGroundTruth = gt;
	}
	@Override
	public String getSettingsString() 
	{
		if (isEnabled)
			return type + FieldDelimiter + "1" + FieldDelimiter + scanIntervalInMs;
		else
			return type + FieldDelimiter + "0" + FieldDelimiter + scanIntervalInMs;
	}
	
	public void stop()
	{	
		locationManager.removeUpdates(locationListener);
		logger.flushFile(type);
	}
	
	@Override
	public String getDebugStatus() 
	{
		return type + FieldDelimiter + debugStatus;
	}
	
	private class GPSLocationListener implements LocationListener 
    {
        public void onLocationChanged(Location loc) 
        {	
        	System.out.println("GPS scan received");
        	String record = gpsStatusCode + PayloadFieldDelimiter + loc.getTime() + PayloadFieldDelimiter +
        					loc.getLatitude() + PayloadFieldDelimiter + loc.getLongitude() + PayloadFieldDelimiter + 
        					loc.getAltitude() + PayloadFieldDelimiter + loc.getAccuracy() + PayloadFieldDelimiter + 
        					loc.getSpeed() + PayloadFieldDelimiter + loc.getBearing() + PayloadFieldDelimiter+curGroundTruth;;
        	
        	String timestamp = System.currentTimeMillis() + "";
        	logger.writeRecord(type, timestamp, record);
        	debugStatus = LifeLogService.getReadableCurrentTime();
        }
           
        public void onProviderDisabled(String provider) 
        {
            // TODO Auto-generated method stub
        }

        public void onProviderEnabled(String provider) 
        {
            // TODO Auto-generated method stub
        }

        public void onStatusChanged(String provider, int status, Bundle extras) 
        {
        	gpsStatusCode = status; 
        	System.out.println(gpsStatusCode);
        }
    }
}
