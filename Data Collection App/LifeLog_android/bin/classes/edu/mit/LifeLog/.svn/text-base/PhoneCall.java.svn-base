package edu.mit.LifeLog;

import android.content.Context;
import android.database.Cursor;
import android.os.Handler;

public class PhoneCall implements Sensor 
{
	private Logger logger;
	private boolean isEnabled;
	private int scanIntervalInSec;
	private SensorType type;
	private Context context;
	private String debugStatus;
	private Handler callHandler;
	private long lastScannedTime;
	
	public PhoneCall(Context context, Logger logger)
	{
		this.context = context;
		this.logger = logger;
		this.isEnabled = false;
		this.type = SensorType.PhoneCall;
		this.scanIntervalInSec = 0;
		this.debugStatus = "no status";
		this.callHandler = new Handler();
		this.lastScannedTime = 0;
		
        // default setting
        changeSettings(type + FieldDelimiter + "1" + FieldDelimiter + "600");
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
			throw new RuntimeException("wrong setting string for phone call: " + settings);
		
		// cancel the current scanning 
		callHandler.removeCallbacks(callLogScanTask);
		
		this.isEnabled = (splitted[1].equals("1"));
		this.scanIntervalInSec = Integer.parseInt(splitted[2]);
		System.out.println("change phone call settings to: (" + isEnabled + ", " + scanIntervalInSec + ")");
		if (isEnabled)
			callHandler.postDelayed(callLogScanTask, 0);
		else
			logger.flushFile(type);
	}

	@Override
	public String getSettingsString() 
	{
		if (isEnabled)
			return type + FieldDelimiter + "1" + FieldDelimiter + scanIntervalInSec;
		else
			return type + FieldDelimiter + "0" + FieldDelimiter + scanIntervalInSec;		
	}

	@Override
	public void stop() 
	{
		isEnabled = false;
		callHandler.removeCallbacks(callLogScanTask);		
		logger.flushFile(type);		
	}

	@Override
	public String getDebugStatus() 
	{
		return type + FieldDelimiter + debugStatus;
	}
	
	private Runnable callLogScanTask = new Runnable() 
	{
		@Override
		public void run() 
		{			
			System.out.println("scan call log");
			String [] projection = 
				new String [] { android.provider.CallLog.Calls.CACHED_NAME, 
								android.provider.CallLog.Calls.CACHED_NUMBER_LABEL,
								android.provider.CallLog.Calls.CACHED_NUMBER_TYPE,
								android.provider.CallLog.Calls.DURATION,
								android.provider.CallLog.Calls.NEW,
								android.provider.CallLog.Calls.NUMBER,
								android.provider.CallLog.Calls.TYPE,
								android.provider.CallLog.Calls.DATE };
			
			String selection = android.provider.CallLog.Calls.DATE + " > " + lastScannedTime;
			
			Cursor cursor = context.getContentResolver().query(android.provider.CallLog.Calls.CONTENT_URI, projection,
															   selection, null, null);

			cursor.moveToFirst();
			
			int [] projectedColumnIndices = new int[projection.length];
			for (int i = 0; i < projection.length; ++i)
				projectedColumnIndices[i] = cursor.getColumnIndex(projection[i]);
			
			while (!cursor.isAfterLast()) 
			{
				String record = "";
				String timestamp = cursor.getString(projectedColumnIndices[projectedColumnIndices.length - 1]);
				// don't store timestamp in payload
				for (int i = 0; i < projectedColumnIndices.length - 1; ++i)
				{
					if (i != 0) record += PayloadFieldDelimiter;
					record += cursor.getString(projectedColumnIndices[i]);
				}
					
				logger.writeRecord(type, timestamp, record);
				System.out.println("phone log entry: " + record);
				cursor.moveToNext();
			}		

			lastScannedTime = System.currentTimeMillis();
			debugStatus = LifeLogService.getReadableCurrentTime(lastScannedTime);
			cursor.close();

			callHandler.postDelayed(callLogScanTask, scanIntervalInSec * 1000);			
			
		}		
	};

}
