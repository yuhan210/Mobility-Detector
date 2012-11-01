package edu.mit.LifeLog;

import android.content.Context;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;

public class NWLoc implements Sensor
{
	private LocationManager locationManager;
    private LocationListener locationListener;
	private Context context;

	//private WifiManager wifiManager;
	//private WifiStateReceiver wifiStateReceiver;

	//Timer wifiTimer;
	//private long wifiTimerPeriod = 90000;
	
	private int NWStatusCode = 0;
	private static int curGroundTruth;
	private String debugStatus;
	private Logger logger;
	private boolean isEnabled;
	private int scanIntervalInMs;
	private SensorType type;

	public NWLoc(Context ctx, Logger logger)
	{
		this.context = ctx;
		this.logger = logger;
		this.locationManager = (LocationManager)context.getSystemService(Context.LOCATION_SERVICE);
		this.locationListener = new NWLocationListener();
		//this.wifiManager = (WifiManager)context.getSystemService(Context.WIFI_SERVICE);
    	//this.wifiStateReceiver = new WifiStateReceiver();
    	this.debugStatus = "no status";
    	this.isEnabled = false;
    	this.scanIntervalInMs = 0;
    	this.type = SensorType.NWLoc;    	
    	
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
			throw new RuntimeException("wrong setting string for nwloc: " + settings);
		
		// cancel the current scanning 
		locationManager.removeUpdates(locationListener);
		
		this.isEnabled = (splitted[1].equals("1"));
		this.scanIntervalInMs = Integer.parseInt(splitted[2]);
		System.out.println("change nwloc settings to: (" + isEnabled + ", " + scanIntervalInMs + ")");
		if (isEnabled)
		   	locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, scanIntervalInMs, 0, locationListener);
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
	
	@Override
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
	
	private class NWLocationListener implements LocationListener 
    {
        public void onLocationChanged(Location loc) 
        {
        	System.out.println("received nwloc data");
        	String record = NWStatusCode + PayloadFieldDelimiter + loc.getTime() + PayloadFieldDelimiter +
        					loc.getLatitude() + PayloadFieldDelimiter + loc.getLongitude() + PayloadFieldDelimiter + 
        					loc.getAltitude() + PayloadFieldDelimiter + loc.getAccuracy() + PayloadFieldDelimiter + 
        					loc.getSpeed() + PayloadFieldDelimiter + loc.getBearing() +PayloadFieldDelimiter + curGroundTruth;
        	
        	logger.writeRecord(type, System.currentTimeMillis() + "", record);
        	
        	debugStatus = LifeLogService.getReadableCurrentTime(); 
        	//"(" + (int)loc.getLatitude() + " " + (int)loc.getLongitude() + ")";  
        	
        	// Got one location, so go back to sleep now.
        	//locationManager.removeUpdates(this);
        	//wifiManager.setWifiEnabled(false);
        }
                   
        public void onProviderDisabled(String provider) 
        {
        	System.out.println("provider disabled");
            // TODO Auto-generated method stub
        }

        public void onProviderEnabled(String provider) 
        {
        	System.out.println("provider enabled");
            // TODO Auto-generated method stub
        }

        public void onStatusChanged(String provider, int status, Bundle extras) 
        {
        	System.out.println("status changed");
        	NWStatusCode = status;
        }
    }

	/*
	
	public boolean start(int period)
	{	
		//wifiTimerPeriod = period;				
		//wifiTimer = new Timer();
		//wifiTimer.schedule(new WifiTask(), 0, wifiTimerPeriod);			
    	//context.registerReceiver(wifiStateReceiver, new IntentFilter(WifiManager.WIFI_STATE_CHANGED_ACTION));
    	locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 1000, 0, locationListener);
    	
		return true;		
	}
	 
	class WifiStateReceiver extends BroadcastReceiver 
	{
	    public void onReceive(Context c, Intent intent) 
	    {
			//long ms = System.currentTimeMillis();
			//if (wifiManager.getWifiState() == WifiManager.WIFI_STATE_ENABLED) {
			//	writeToFile("" + System.currentTimeMillis() + " wifi_enabled");
			//	locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 1000, 0, locationListener);
			//} else if (wifiManager.getWifiState() == WifiManager.WIFI_STATE_DISABLED) {
			//	writeToFile("" + System.currentTimeMillis() + " wifi_disabled");
			//}
	    } 
	}
	
	class WifiTask extends TimerTask
	{
		public void run()
		{
			if (wifiManager.getWifiState() != WifiManager.WIFI_STATE_ENABLED) {
				wifiManager.setWifiEnabled(true);
			}
		}
	}
	*/
}
