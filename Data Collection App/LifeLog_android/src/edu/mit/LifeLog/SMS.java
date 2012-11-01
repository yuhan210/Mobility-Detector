package edu.mit.LifeLog;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.telephony.SmsMessage;

public class SMS implements Sensor
{
	private Logger logger;
	private SensorType type;
	private Context context;
	private String debugStatus;
	private boolean isEnabled;
	
	public SMS(Context context, Logger logger)
	{
		this.context = context;
		this.logger = logger;
		this.isEnabled = false;
		//this.type = SensorType.SMS;
		this.debugStatus = "no status";
		
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
			throw new RuntimeException("wrong setting string for sms: " + settings);
		
		boolean newIsEnabled = (splitted[1].equals("1"));
		if (isEnabled != newIsEnabled)
		{
			if (newIsEnabled)
			{			
				context.registerReceiver(smsReceiver, new IntentFilter("android.provider.Telephony.SMS_RECEIVED"));
				context.registerReceiver(smsReceiver, new IntentFilter("android.provider.Telephony.SMS_SENT"));
			}
			else
			{
				context.unregisterReceiver(smsReceiver);
				logger.flushFile(type);
			}
		}

		this.isEnabled = newIsEnabled;
		System.out.println("change sms settings to: (" + isEnabled + ")");
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
			context.unregisterReceiver(smsReceiver);
		logger.flushFile(type);	
	}

	@Override
	public String getDebugStatus() 
	{
		return type + FieldDelimiter + debugStatus;
	}

	private BroadcastReceiver smsReceiver = new BroadcastReceiver()
	{
		@Override
		public void onReceive(Context context, Intent intent) 
		{
			Bundle bundle = intent.getExtras();
			if (bundle != null)
			{
				Object [] pdus = (Object []) bundle.get("pdus");
				SmsMessage [] messages = new SmsMessage[pdus.length];
				for (int i = 0; i < messages.length; ++i)
				{
					SmsMessage m = SmsMessage.createFromPdu((byte [])pdus[i]);
					String record = m.getOriginatingAddress() + PayloadFieldDelimiter + m.getMessageBody();
					String timestamp = m.getTimestampMillis() + "";
					logger.writeRecord(type, timestamp, record);
					System.out.println("sms message: " + record);
				}	
				debugStatus = LifeLogService.getReadableCurrentTime();
			}
		}
	};
}
