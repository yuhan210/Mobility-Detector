package edu.mit.LifeLog;

import android.content.Context;
import android.database.Cursor;
import android.os.Handler;

public class Browser implements Sensor 
{
	private Context context;
	private Logger logger;
	private boolean isEnabled;
	private int scanIntervalInSec;
	private String debugStatus;
	private SensorType type;
	private Handler browserHandler;
	private long lastScannedTime;
	private static int curGroundTruth;

	
	public Browser(Context context, Logger logger)
	{
		this.context = context;
		this.logger = logger;
		this.isEnabled = false;
		this.scanIntervalInSec = 0;
		this.debugStatus = "no status";
		this.type = SensorType.Browser;
		this.browserHandler = new Handler();
		this.lastScannedTime = 0;
		this.curGroundTruth = 0;
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
			throw new RuntimeException("wrong setting string for browser: " + settings);
		
		// cancel the current scanning 
		browserHandler.removeCallbacks(browserDataScanTask);
		
		this.isEnabled = (splitted[1].equals("1"));
		this.scanIntervalInSec = Integer.parseInt(splitted[2]);
		System.out.println("change browser settings to: (" + isEnabled + ", " + scanIntervalInSec + ")");
		if (isEnabled)
			browserHandler.postDelayed(browserDataScanTask, 0);
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
			return type + FieldDelimiter + "1" + FieldDelimiter + scanIntervalInSec;
		else
			return type + FieldDelimiter + "0" + FieldDelimiter + scanIntervalInSec;		
	}

	@Override
	public void stop()
	{
		isEnabled = false;
		browserHandler.removeCallbacks(browserDataScanTask);
		logger.flushFile(type);		
	}

	@Override
	public String getDebugStatus() 
	{
		return type + FieldDelimiter + debugStatus;
	}
	
	private Runnable browserDataScanTask = new Runnable() 
	{
		@Override
		public void run() 
		{
			System.out.println("scan browser history");
			String[] projection = new String[] { android.provider.Browser.BookmarkColumns.TITLE, 
												 android.provider.Browser.BookmarkColumns.URL,
												 android.provider.Browser.BookmarkColumns.DATE }; 
			
			
			String selection = android.provider.Browser.BookmarkColumns.BOOKMARK + " = 0 AND " + 
							   android.provider.Browser.BookmarkColumns.DATE + " > " + lastScannedTime;
			
			// only want the non bookmarked items (i.e., history)
			Cursor cursor = context.getContentResolver().query(android.provider.Browser.BOOKMARKS_URI, projection, 
															   selection, null, null);
			
			cursor.moveToFirst();
			
			int [] projectedColumnIndices = new int[projection.length];
			for (int i = 0; i < projection.length; ++i)
				projectedColumnIndices[i] = cursor.getColumnIndex(projection[i]);
			
			while (!cursor.isAfterLast()) 
			{
				String record = "";
				String timestamp = cursor.getString(projectedColumnIndices[projectedColumnIndices.length - 1]);
				
				// don't save the timestamp in payload
				for (int i = 0; i < projectedColumnIndices.length - 1; ++i)
				{
					if (i != 0) record += PayloadFieldDelimiter;
					record += cursor.getString(projectedColumnIndices[i]);
				}
					
				logger.writeRecord(type, timestamp, record);
				System.out.println("browser history: " + record);
				cursor.moveToNext();
			}		
			
			lastScannedTime = System.currentTimeMillis();
			debugStatus = LifeLogService.getReadableCurrentTime(lastScannedTime);
			cursor.close();
			
			browserHandler.postDelayed(browserDataScanTask, scanIntervalInSec * 1000);
		}		
	};
}
