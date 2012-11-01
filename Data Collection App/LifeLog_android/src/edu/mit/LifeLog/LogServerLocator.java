package edu.mit.LifeLog;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import android.content.Context;
import android.widget.Toast;

public class LogServerLocator implements Sensor
{
	private String debugStatus;
	private Context context;
	private SensorType type;
	private String ip;
	private int port;
	
	private static final String HAMMER_IP = "128.30.76.165"; // default to hammer.csail.mit.edu
	private static final int HAMMER_PORT = 44444;
	private static final String PortDelimiter = "#";
	
	public LogServerLocator (Context context, Logger logger)
	{
		this.context = context;
		//this.type = SensorType.LogServerLocator;
		this.debugStatus = "no status";
		
        // default setting
        changeSettings(type + FieldDelimiter + HAMMER_IP + PortDelimiter + HAMMER_PORT);
	}
	
	@Override
	public SensorType getType() 
	{
		return type;
	}
	
	public String getServerIP ()
	{
		return this.ip;
	}
	
	public int getServerPort ()
	{
		return this.port;
	}

	@Override
	public void changeSettings(String settings) 
	{
		String [] splitted = settings.split(FieldDelimiter);
		boolean changeSucceeded = false;
		
		if (splitted.length != 2 || !splitted[0].equals(type.toString()))			
			throw new RuntimeException("wrong setting string for server locator: " + settings);

		String [] ipAndPort = splitted[1].split(PortDelimiter);
		if (isValidIP(ipAndPort[0]))
			this.ip = ipAndPort[0];
		else
		{
			System.out.println(ipAndPort[0] + " is not a valid ip");
			Toast.makeText(this.context, "Please input a valid ip address", Toast.LENGTH_SHORT).show();
		}
		
		try 
		{ 
			this.port = Integer.parseInt(ipAndPort[1]); 
			changeSucceeded = true;
		}
		catch (NumberFormatException e)
		{ Toast.makeText(this.context, "Please input a valid port number", Toast.LENGTH_SHORT).show(); }
		
		if (changeSucceeded)
		{
			System.out.println("change server locator settings to: (" + ip + PortDelimiter + port + ")");
			try { throw new Exception(); } 
			catch (Exception e) { e.printStackTrace(); }
			this.debugStatus = this.ip + ":" + this.port;
		}
	}

	@Override
	public String getSettingsString() 
	{
		return type + FieldDelimiter + ip + PortDelimiter + port;		
	}

	@Override
	public void stop() 
	{
		// nothing
	}

	@Override
	public String getDebugStatus() 
	{
		return type + FieldDelimiter + debugStatus;
	}

	private static final Pattern ipPattern = Pattern.compile("\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}");
	private boolean isValidIP (String s)
	{
		Matcher m = ipPattern.matcher(s);
		return m.matches();
	}
}
