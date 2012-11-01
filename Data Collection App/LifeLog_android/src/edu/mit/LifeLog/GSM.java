package edu.mit.LifeLog;

import java.util.List;
import java.util.Timer;
import java.util.TimerTask;

import android.content.Context;
import android.telephony.CellLocation;
import android.telephony.NeighboringCellInfo;
import android.telephony.PhoneStateListener;
import android.telephony.SignalStrength;
import android.telephony.TelephonyManager;
import android.telephony.gsm.GsmCellLocation;

public class GSM implements Sensor
{
	private TelephonyManager telephonyManager;
	private Context context;
	private Timer timer;
	private Logger logger;	
	private SensorType type;
	private boolean isEnabled;
	private int scanIntervalInMs;
	private static int curGroundTruth;
	
	private int connectedTowerRSSI = 0;
	
	private String debugStatus;
	
	public GSM(Context ctx, Logger logger)
	{
		this.context = ctx;
		this.logger = logger;
		this.telephonyManager = (TelephonyManager)context.getSystemService(Context.TELEPHONY_SERVICE);
		this.timer = new Timer();
		
		this.type = SensorType.GSM;
		this.debugStatus = "no status";
		this.scanIntervalInMs = 0;
		this.isEnabled = false;
		
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
			throw new RuntimeException("wrong setting string for gsm: " + settings);
		
		// cancel the current scanning 
		timer.cancel();
		
		this.isEnabled = (splitted[1].equals("1"));
		this.scanIntervalInMs = Integer.parseInt(splitted[2]);
		System.out.println("change GSM settings to: (" + isEnabled + ", " + scanIntervalInMs + ")");
		if (isEnabled)
		{
			timer = new Timer();
			timer.schedule(new GSMTask(), 0, scanIntervalInMs);
			telephonyManager.listen(phoneStateListner, PhoneStateListener.LISTEN_SIGNAL_STRENGTHS | PhoneStateListener.LISTEN_CELL_LOCATION);
		
		}
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
		telephonyManager.listen(phoneStateListner, PhoneStateListener.LISTEN_NONE);
		timer.cancel();
		logger.flushFile(type);
	}

	@Override
	public String getDebugStatus() 
	{
		return type + FieldDelimiter + debugStatus;
	}

	class GSMTask extends TimerTask 
	{		
		public void run() 
	    {
			System.out.println("GSM scan received");
			GsmCellLocation gloc = (GsmCellLocation)telephonyManager.getCellLocation();
			String record;
			
	        if (gloc != null) 
	        {
	        	record = gloc.getCid() + PayloadFieldDelimiter + gloc.getLac() + PayloadFieldDelimiter + 
	        	         connectedTowerRSSI + PayloadFieldDelimiter + 
	        	         telephonyManager.getNetworkType() + PayloadFieldDelimiter + telephonyManager.getDataState() + PayloadFieldDelimiter + curGroundTruth + PayloadFieldDelimiter;
	        }
	        else
	        {
	        	record = "-1" + PayloadFieldDelimiter + "-1" + PayloadFieldDelimiter + connectedTowerRSSI + PayloadFieldDelimiter +
						  telephonyManager.getNetworkType() + PayloadFieldDelimiter + telephonyManager.getDataState() + PayloadFieldDelimiter + curGroundTruth + PayloadFieldDelimiter;
	        }
	        
	        List<NeighboringCellInfo> lstNCell = telephonyManager.getNeighboringCellInfo();
	        
	        record += lstNCell.size();
	    	for (int i = 0; i < lstNCell.size(); i++)
	        {
	        	record += PayloadFieldDelimiter + lstNCell.get(i).getCid() + PayloadFieldDelimiter  + lstNCell.get(i).getLac() + PayloadFieldDelimiter+ lstNCell.get(i).getRssi();
	        }	    	
	    	logger.writeRecord(type, System.currentTimeMillis() + "", record);	
	    	debugStatus = LifeLogService.getReadableCurrentTime();
	    }

	}
	
	private PhoneStateListener phoneStateListner = new PhoneStateListener()
	{
		public void  onSignalStrengthsChanged(SignalStrength asu)
		{
			connectedTowerRSSI = asu.getGsmSignalStrength();
		}
		
		public void  onCellLocationChanged  (CellLocation location)
		{
			
		}
	};
}
