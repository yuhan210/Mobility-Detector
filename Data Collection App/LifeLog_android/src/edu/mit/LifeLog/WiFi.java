package edu.mit.LifeLog;

import java.util.List;
import java.util.Timer;
import java.util.TimerTask;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.provider.Settings;

public class WiFi implements Sensor
{
	private WifiManager wifiManager;
	private WifiReceiver wifiReceiver;
	private Context context;
	private Timer timer;
	private Logger logger;	
	private boolean isEnabled;
	private int scanIntervalInMs;
	private SensorType type;
	private String debugStatus;
	private static int curGroundTruth;
	
	public WiFi(Context ctx, Logger logger)
	{
		this.context = ctx;		
		this.logger = logger;		
		this.wifiManager = (WifiManager)context.getSystemService(Context.WIFI_SERVICE);
		boolean result = Settings.System.putInt(ctx.getContentResolver(), 
				                                Settings.System.WIFI_SLEEP_POLICY, 
				                                Settings.System.WIFI_SLEEP_POLICY_NEVER);
		System.out.println("result: " + result);
		this.wifiReceiver = new WifiReceiver();
		this.isEnabled = false;
		this.scanIntervalInMs = 0;
		this.type = SensorType.Wifi;
		this.debugStatus = "no status";	
		this.timer = new Timer();
		
        // default setting
        changeSettings(type + FieldDelimiter + "1" + FieldDelimiter + "1000");
	}
	public static void setGroundTruth(int gt){
		   curGroundTruth = gt;
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
			throw new RuntimeException("wrong setting string for wifi: " + settings + " len: " + splitted.length + " 0: " + splitted[0]);
		
		// cancel the current scanning 
		timer.cancel();
		
		this.isEnabled = (splitted[1].equals("1"));
		this.scanIntervalInMs = Integer.parseInt(splitted[2]);
		System.out.println("change wifi settings to: (" + isEnabled + ", " + scanIntervalInMs + ")");
		if (isEnabled)
		{
			this.timer = new Timer();
			TimerTask ts = new TimerTask() { public void run() { wifiManager.startScan(); } };					
		
			timer.schedule(ts, 0, scanIntervalInMs);
			context.registerReceiver(wifiReceiver, new IntentFilter(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION));
		}
		else
			logger.flushFile(type);
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
		if (isEnabled)
			context.unregisterReceiver(wifiReceiver);		
		timer.cancel();
		logger.flushFile(type);
	}
	
	@Override
	public String getDebugStatus()
	{
		return getType() + FieldDelimiter + debugStatus;
	}
	
	public String getWiFiMAC()
	{
		return wifiManager.getConnectionInfo().getMacAddress();
	}
		
	class WifiReceiver extends BroadcastReceiver 
	{
	    public void onReceive(Context c, Intent intent) 
	    {
	    	System.out.println("wifi scan received");
			
	    	WifiInfo wifiInfo = wifiManager.getConnectionInfo();
	    	List<ScanResult> scanResults = wifiManager.getScanResults();

	    	String record = wifiManager.getWifiState() + PayloadFieldDelimiter + 
	    	         		wifiInfo.getSSID() + PayloadFieldDelimiter + 
	    	         		wifiInfo.getBSSID() + PayloadFieldDelimiter + 
	    	         		wifiInfo.getRssi() + PayloadFieldDelimiter + scanResults.size() + PayloadFieldDelimiter + curGroundTruth;
	    	
	    	for (int i = 0; i < scanResults.size(); i++)
	    	{
	    		record += PayloadFieldDelimiter + scanResults.get(i).SSID + PayloadFieldDelimiter + 
	    		          scanResults.get(i).BSSID + PayloadFieldDelimiter + 
	    		          scanResults.get(i).level + PayloadFieldDelimiter + scanResults.get(i).frequency;
	    	}

	    	logger.writeRecord(type, System.currentTimeMillis() + "", record);
	    	debugStatus = LifeLogService.getReadableCurrentTime(); //scanResults.size() + "";
	    }
	}


	
	
	/*
	
	class WifiTask extends TimerTask 
	{
		public void run() 
	    {
			if (Settings.WiFiScanEnabled)
			{
				wifiManager.startScan();
			}
			else
			{
				long ms = System.currentTimeMillis();
		    	String record = ms + " ";
		    	WifiInfo wifiInfo = wifiManager.getConnectionInfo();
		    	List<ScanResult> scanResults = wifiManager.getScanResults();

		    	record = record + wifiManager.getWifiState();
		    	record = record + "|" + wifiInfo.getSSID() + "|" + wifiInfo.getBSSID() + "|" + wifiInfo.getRssi();
		    	record = record + "|" + scanResults.size();
		    	for (int i = 0; i < scanResults.size(); i++)
		    	{
		    		record = record + "|" + scanResults.get(i).SSID + "|" + scanResults.get(i).BSSID +
		    			"|" + scanResults.get(i).level + "|" + scanResults.get(i).frequency;
		    	}
		    	writeToFile(record);
		    	status = scanResults.size() + "";
			}			
	    }
	}
	*/	
}
