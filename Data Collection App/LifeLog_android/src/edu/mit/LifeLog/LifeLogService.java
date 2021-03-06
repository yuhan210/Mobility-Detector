package edu.mit.LifeLog;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.hardware.SensorManager;
import android.os.Handler;
import android.os.IBinder;
import android.os.Message;
import android.os.Messenger;
import android.os.PowerManager;
import android.os.RemoteException;
import android.telephony.TelephonyManager;
import android.widget.Toast;

import edu.mit.LifeLog.Sensor.SensorType;

public class LifeLogService extends Service
{
	static final String ConfigLocal = "/sdcard/LifeLogConfig/";
	
	static final String DataDir = "/sdcard/LifeLogData/";
	static final String DebugDir = "/sdcard/LifeLogDebug/";
	static final String DataStagingDir = "/sdcard/LifeLogData-staging";
	static String CurDataDir = "/sdcard/LifeLogData";
		
	static final String RequestFilename = "settingsRequest.txt";
	static final String ResponseFilename = "settingsResponse.txt";
	static final String DefaultSettingsFilename = "defaultSettings.txt";
	static final String DebugMsgFilename = "debug.txt";
	
	static final String RequestFile = ConfigLocal + RequestFilename;
	static final String ResponseFile = ConfigLocal + ResponseFilename;
	static final String DefaultSettingsFile = ConfigLocal + DefaultSettingsFilename;
	
	static final String DebugMsgFile = DebugDir + DebugMsgFilename;
	
	static final String FileDelimiter = ","; 	
	
	// RPC call numbers
    static final int MSG_STATUS_QUERY = 1;
    static final int MSG_CHANGE_SETTINGS = 2;
    
    // number of ms between each debug print
    private static final int DebugPrintInterval = 1000;

    private HashMap<SensorType, Sensor> sensors;           
    private final Messenger mMessenger = new Messenger(new IncomingHandler());    
    
    private Logger logger;
    private Handler printHandler;
    private boolean hasStarted = false;
    private PowerManager.WakeLock wakelock;

    
    @Override
    public void onCreate() 
    {   
    	if (hasStarted) return;

    	PowerManager power = (PowerManager) getSystemService(Context.POWER_SERVICE);
    	wakelock = power.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "My Tag");
    	wakelock.acquire();

    	System.out.println("power lock held: " + wakelock.isHeld());
    	 
    	hasStarted = true;
    	
    	SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd-HH-mm-ss");        
        String currentTime = dateFormat.format(new Date());
        System.out.println("LifeLog service starts now: " + currentTime);
        CurDataDir = CurDataDir+"/"+currentTime+"/";
        
    	// set up the logger
    	new File(DataDir).mkdir();    
    	new File(DataStagingDir).mkdir();    
        new File(ConfigLocal).mkdir(); 
        new File(DebugDir).mkdir();
        new File(CurDataDir).mkdir();
        
        TelephonyManager tManager = (TelephonyManager)getSystemService(Context.TELEPHONY_SERVICE);
        String phoneId = tManager.getDeviceId();
        this.logger = new Logger(CurDataDir, currentTime, phoneId);
                
        // create the sensors
		SensorManager sensorManager = (SensorManager)getSystemService(Context.SENSOR_SERVICE);
		PackageManager pm = getPackageManager();
		
        this.sensors = new HashMap<SensorType, Sensor>();

        if (pm.hasSystemFeature(PackageManager.FEATURE_LOCATION_GPS))
        	sensors.put(SensorType.GPS, new GPS(this, logger));
        if (pm.hasSystemFeature(PackageManager.FEATURE_WIFI))
        	sensors.put(SensorType.Wifi, new WiFi(this, logger));
        if (pm.hasSystemFeature(PackageManager.FEATURE_TELEPHONY_GSM))
        	sensors.put(SensorType.GSM, new GSM(this, logger));
       // if (pm.hasSystemFeature(PackageManager.FEATURE_WIFI)) // connect to hammer
       // 	sensors.put(SensorType.Downlink, new Downlink("128.30.76.165", 44443, this, logger));
		if (pm.hasSystemFeature(PackageManager.FEATURE_LOCATION_NETWORK))
			sensors.put(SensorType.NWLoc, new NWLoc(this, logger));
		
		sensors.put(SensorType.Browser, new Browser(this, logger));
		sensors.put(SensorType.PhoneCall, new PhoneCall(this, logger));		
			
        if (pm.hasSystemFeature(PackageManager.FEATURE_SENSOR_ACCELEROMETER))	
            sensors.put(SensorType.Accl, new Accl(this, logger));			
	    //if (pm.hasSystemFeature(PackageManager.FEATURE_SENSOR_COMPASS))
	    //    sensors.put(SensorType.Compass, new Compass(this, logger));
		if (sensorManager.getSensorList(android.hardware.Sensor.TYPE_ORIENTATION).size() != 0)		
	        sensors.put(SensorType.Ort, new Ort(this, logger));     
		if (sensorManager.getSensorList(android.hardware.Sensor.TYPE_PROXIMITY).size() != 0)		
	        sensors.put(SensorType.Proximity, new Proximity(this, logger));    
		if (sensorManager.getSensorList(android.hardware.Sensor.TYPE_LIGHT).size() != 0)		
	        sensors.put(SensorType.Light, new Light(this, logger));	
		//if (pm.hasSystemFeature(PackageManager.FEATURE_BLUETOOTH))
		//	sensors.put(SensorType.Bluetooth, new Bluetooth(this, logger));
		//if (pm.hasSystemFeature(PackageManager.FEATURE_CAMERA))
		//	sensors.put(SensorType.Camera, new Camera(this, logger));
		if (sensorManager.getSensorList(android.hardware.Sensor.TYPE_GYROSCOPE).size() != 0)
			sensors.put(SensorType.GYRO, new GYRO(this, logger));
		
		//sensors.put(SensorType.SMS, new SMS(this, logger));
		//sensors.put(SensorType.LogUploader, new LogUploader(this, logger));
		//sensors.put(SensorType.SMS, new SMS(this, logger));
	//	LogServerLocator serverLocator = new LogServerLocator(this, logger);
		//sensors.put(SensorType.LogUploader, new LogUploader(this, logger, serverLocator));
		//sensors.put(SensorType.LogServerLocator, serverLocator);
		//sensors.put(SensorType.TouchScreen, new TouchScreen(this,logger));
    	setupSensors();
    	
    	// delete the previous debug log if exists, and set up the debug status handler
		File f = new File(DebugMsgFile);
		f.delete();
        this.printHandler = new Handler();
    	printHandler.postDelayed(printStatusTask, 0);
    	
        Toast.makeText(this, "LifeLog service started", Toast.LENGTH_SHORT).show();        
    }    
    
	private void setupSensors()
	{			
        try
        {
        	BufferedReader r = new BufferedReader(new FileReader(DefaultSettingsFile));
        	String line;
        	while ((line = r.readLine()) != null)
        	{
				if (line.startsWith(Sensor.CommentDelimiter)) continue;
				String [] splitted = line.split(FileDelimiter);
				
				SensorType type = SensorType.getSensorType(splitted[0]);
				Sensor sensor = sensors.get(type);
				if (sensor == null)
					throw new RuntimeException("cannot find sensor type in settings file: " + line);
				
				sensor.changeSettings(line);				
        	}
        	r.close();
        }
        catch (IOException e) { System.out.println("default settings file not found"); }						
	}
	
    @Override
    public void onDestroy() 
    {
        System.out.println("service destroyed");        
        stopSensors();
		printHandler.removeCallbacks(printStatusTask);        
		wakelock.release();
        Toast.makeText(this, "LifeLog service stopped", Toast.LENGTH_SHORT).show();
        System.runFinalizersOnExit(true);
        System.exit(0);
    }
    
	private void stopSensors()
	{
		for (Sensor s : sensors.values())
			s.stop();		
	}	
    
    @Override
    public IBinder onBind(Intent intent) 
    {
        return mMessenger.getBinder();
    }

    @Override
    public boolean onUnbind(Intent intent)
    {
    	Toast.makeText(this, "LifeLog service unbound", Toast.LENGTH_SHORT).show();
    	return false;
    }
	
	private Runnable printStatusTask = new Runnable() 
	{			
		public void run() 
		{		
			try
			{
				BufferedWriter log = new BufferedWriter(new FileWriter(DebugMsgFile, false), 10000);
			
				for (Sensor s : sensors.values())
					log.write(s.getDebugStatus() + "\n");
				
				log.close();
			} 
			catch (IOException e) { throw new RuntimeException(e); }
				
			printHandler.postDelayed(printStatusTask, DebugPrintInterval);						
		}
	};
    	
    
    class IncomingHandler extends Handler 
    {
        @Override
        public void handleMessage(Message msg) 
        {
            switch (msg.what) 
            {
            case MSG_STATUS_QUERY:
            	System.out.println("got status query msg");
            	try 
            	{ 
            		Message m = Message.obtain(null, MSG_STATUS_QUERY);
            		writeSensorSettingsToFile(ResponseFile);        
            		msg.replyTo.send(m); 
            	}
            	catch (RemoteException deadClient) {}
            	break;
            case MSG_CHANGE_SETTINGS:
            	System.out.println("got change settings msg");
            	//try
            	{
            		changeSensorSettings(RequestFile);
               		// also write to the default settings file so that on reboot it will use the 
            		// last settings
            		writeSensorSettingsToFile(DefaultSettingsFile);
            		/*
            		Message m = Message.obtain(null, MSG_STATUS_QUERY);
            		writeSensorSettingsToFile(ResponseFilename);
            		msg.replyTo.send(m);
            		*/
            	}
            	//catch (RemoteException deadClient) {}            	
            	break;
            default:
            	super.handleMessage(msg);
            }
        }
        
        private void changeSensorSettings(String filename)
        {
        	try
        	{
        		BufferedReader r = new BufferedReader(new FileReader(filename), 1000);
        		String line;
        		while ((line = r.readLine()) != null)
        		{
        			System.out.println("line read: " + line);
        			String [] splitted = line.split(FileDelimiter);
        			Sensor sensor = sensors.get(SensorType.getSensorType(splitted[0]));
        			if (sensor == null)
        				throw new RuntimeException("cannot change settings for sensor: " + line);
        			sensor.changeSettings(line);
        		}
        	}        	
        	catch (IOException e) { throw new RuntimeException(e); }
        }
        
        private void writeSensorSettingsToFile(String filename)
        {
			System.out.println("writing to file");
			try
			{
				BufferedWriter w = new BufferedWriter(new FileWriter(filename), 1000);
				for (Sensor s : sensors.values())				
					w.write(s.getSettingsString() + "\n");					
    				    			
				w.close();    			    		

    		}
			catch (IOException e) { throw new RuntimeException(e); }			    		
        }
    }	
    
    private static final String DATE_FORMAT_NOW = "yyyy-MM-dd HH:mm:ss";

    // for debug
    public static String getReadableCurrentTime() 
    {
    	Calendar cal = Calendar.getInstance();
    	SimpleDateFormat sdf = new SimpleDateFormat(DATE_FORMAT_NOW);
    	return sdf.format(cal.getTime());
    }
    
    public static String getReadableCurrentTime(long timeToFormat) 
    {
    	SimpleDateFormat sdf = new SimpleDateFormat(DATE_FORMAT_NOW);
    	return sdf.format(new Date(timeToFormat));
    }
}
