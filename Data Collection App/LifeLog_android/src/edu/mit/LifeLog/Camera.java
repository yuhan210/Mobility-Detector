package edu.mit.LifeLog;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.database.Cursor;
import android.net.Uri;
import android.provider.MediaStore;

public class Camera implements Sensor 
{
	private Logger logger;
	private Context context;
	private boolean isEnabled;
	private SensorType type;
	private String debugStatus;

	public Camera(Context context, Logger logger)
	{
		this.context = context;
		this.logger = logger;
		this.isEnabled = false;
		this.debugStatus = "no status";
		//this.type = SensorType.Camera;
		
        // default setting
        changeSettings(type + FieldDelimiter + "1");
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
		if (splitted.length != 2 || !splitted[0].equals(type.toString()))			
			throw new RuntimeException("wrong setting string for camera: " + settings);
		
		boolean newIsEnabled = (splitted[1].equals("1"));
		if (isEnabled != newIsEnabled)
		{
			if (newIsEnabled)
			{
				IntentFilter photoFilter = new IntentFilter("com.android.camera.NEW_PICTURE");
				try { photoFilter.addDataType("*/*"); } 
				catch (Exception e) { throw new RuntimeException("unknown mime type in camera intent filter"); }
				context.registerReceiver(photoReceiver, photoFilter);
			}
			else
			{
				context.unregisterReceiver(photoReceiver);
				logger.flushFile(type);
			}
		}

		this.isEnabled = newIsEnabled;
		System.out.println("change camera settings to: (" + isEnabled + ")");
	}

	@Override
	public String getSettingsString() 
	{
		if (isEnabled)
			return type + FieldDelimiter + "1";
		else
			return type + FieldDelimiter + "0";		
	}

	@Override
	public void stop() 
	{
		if (isEnabled)
			context.unregisterReceiver(photoReceiver);
		logger.flushFile(type);	
	}

	@Override
	public String getDebugStatus() 
	{
		return type + FieldDelimiter + debugStatus;
	}
	
	
	private BroadcastReceiver photoReceiver = new BroadcastReceiver()
	{
		@Override
		public void onReceive(Context context, Intent intent) 
		{
			Uri uri = intent.getData();
			String record = getRealPathFromURI(uri);
			System.out.println("photo taken to: " + record);
			String timestamp = System.currentTimeMillis() + "";
			logger.writeRecord(type, timestamp, record);
			// can optionally get the camera parameters from android.hardware.Camera.getParameters()
			debugStatus = LifeLogService.getReadableCurrentTime();
		}
		
		private String getRealPathFromURI(Uri contentUri) 
		{
	        String[] proj = { MediaStore.Images.Media.DATA };
	        Cursor cursor = context.getContentResolver().query(contentUri, proj, null, null, null);
	        int column_index = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATA);
	        cursor.moveToFirst();
	        String path = cursor.getString(column_index);
	        cursor.close();
	        return path;
	    }
	};	
}
