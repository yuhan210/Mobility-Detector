package edu.mit.LifeLog;

import java.io.IOException;
import java.io.InputStream;
import java.net.InetSocketAddress;
import java.net.Socket;

import android.content.Context;
import android.net.wifi.WifiManager;
import android.os.Handler;


public class Downlink implements Sensor
{
	private String ipAddress;
	private int port;
	
	private Logger logger;
	
	private String debugStatus;
	private boolean isEnabled = false;
	private int scanIntervalInSec = 0;
	private SensorType type;
	private Handler downloadHandler;
	private Context context;
	
	public Downlink(String ipAddress, int port, Context context, Logger logger)
	{
		this.ipAddress = ipAddress;
		this.port = port;

		this.debugStatus = "no status";
		//this.type = SensorType.Downlink;
		this.isEnabled = false;
		this.scanIntervalInSec = 0;
		this.logger = logger;
		this.downloadHandler = new Handler();
		this.context = context;
		
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
			throw new RuntimeException("wrong setting string for downlink: " + settings);
		
		// cancel the current scanning 
		downloadHandler.removeCallbacks(downloadTask);
		
		this.isEnabled = (splitted[1].equals("1"));
		this.scanIntervalInSec = Integer.parseInt(splitted[2]);
		System.out.println("change downlink settings to: (" + isEnabled + ", " + scanIntervalInSec + ")");
		if (isEnabled)
			downloadHandler.postDelayed(downloadTask, 0);
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
	public String getDebugStatus() 
	{
		return type + FieldDelimiter + debugStatus;
	}
	
	@Override
	public void stop()
	{
		isEnabled = false;
		downloadHandler.removeCallbacks(downloadTask);
		logger.flushFile(type);
	}
	
	
	private enum DownloadTaskState 
	{ 
		Connect("connect failed"), 
		OpenStream("open failed"), 
		Download("download failed"), 
		Finished("finished");
	
		private String desc;
		private DownloadTaskState(String desc) { this.desc = desc; }
		@Override
		public String toString() { return desc; }
	};
	
	private Runnable downloadTask = new Runnable() 
	{
		private static final int SocketTimeout = 5000;
	
		@Override
		public void run() 
		{			
			boolean hasWifi = ((WifiManager)context.getSystemService(Context.WIFI_SERVICE)).isWifiEnabled();
			System.out.println("wifi enabled: " + hasWifi);
			if (!hasWifi)
			{
				downloadHandler.postDelayed(downloadTask, scanIntervalInSec * 1000);
				return;
			}	
			
			long startTime = System.currentTimeMillis();
			DownloadTaskState state = DownloadTaskState.Connect;
			long totalBytesReceived = 0;
			double throughput = 0;
			
			try
			{				
				Socket socket = new Socket();
				socket.setSoTimeout(SocketTimeout);
				InetSocketAddress socketAddress = new InetSocketAddress(ipAddress, port);
				socket.connect(socketAddress, SocketTimeout);
				
				state = DownloadTaskState.OpenStream;
				
				//ObjectInputStream iStream = new ObjectInputStream(socket.getInputStream());
				//FileOutputStream fos = new FileOutputStream("")
				InputStream iStream = socket.getInputStream();
				
				state = DownloadTaskState.Download;
				byte[] buf = new byte[8192];						
				

				int bytesRead;
				
				while( isEnabled && (bytesRead = iStream.read(buf, 0, 8192)) != -1)
				{
					totalBytesReceived += bytesRead;
					
					/*
					currentTime = System.currentTimeMillis();
					throughput = ((double)totalBytesReceived * 1000) / ((double)currentTime - (double)startTime);
					throughput = (throughput * 8)/1024;
					record = record + currentTime + " receive " + bytesRead;
					writeToFile(record);
					*/
					debugStatus = LifeLogService.getReadableCurrentTime();					
				}
								
				System.out.println("finished download file");
				throughput = totalBytesReceived / (double)(System.currentTimeMillis() - startTime);							
				state = DownloadTaskState.Finished;
			}
			catch (IOException e) 
			{ 
				// in the failure cases this will return 0
				throughput = totalBytesReceived / (double)(System.currentTimeMillis() - startTime); 
			}
			
			long endTime = System.currentTimeMillis();
			String record = startTime + PayloadFieldDelimiter + endTime + PayloadFieldDelimiter + state + 
							PayloadFieldDelimiter + throughput;
			
			System.out.println("write to log: " + record);
			logger.writeRecord(type, endTime + "", record);
			
			downloadHandler.postDelayed(downloadTask, scanIntervalInSec * 1000);
		}		
	};
	
	/*
	
	class DownloadThread extends Thread 
	{		
		public void run() 
	    {
			boolean success = true;
			startTime = System.currentTimeMillis();
			writeToFile(startTime + " start 0");
			
			while (isEnabled)
			{
				Socket socket;
				success = true;
				try
				{
					socket = new Socket();
					socket.setSoTimeout(500);
					InetSocketAddress socketAddress = new InetSocketAddress(ipAddress, port);
					socket.connect(socketAddress, 500);
				}
				catch (Exception e)
				{
					//Log.e("exception", "Error connection to server");
					debugStatus = "connectFail";
					
					currentTime = System.currentTimeMillis();
					writeToFile(currentTime + " connectFail 0");
					
					success = false;
				}
				Log.d("message", "Connection accepted");
				
				
				if (success)
				{
					try
					{
						iStream = new ObjectInputStream(socket.getInputStream());
					}
					catch (Exception e)
					{
						//Log.e("exception", "error creating input stream");
						
						debugStatus = "streamFail";
						
						currentTime = System.currentTimeMillis();
						writeToFile(currentTime + " streamFail 0");
						
						success = false;
					}
				}
				
				if (success)
				{
					try
					{
						byte[] buf = new byte[8192];						
						while(true)
						{
							String record = "";
							int bytesRead = iStream.read(buf, 0, 8192);
							totalBytesReceived += bytesRead;
							currentTime = System.currentTimeMillis();
							throughput = ((double)totalBytesReceived * 1000) / ((double)currentTime - (double)startTime);
							throughput = (throughput * 8)/1024;
							record = record + currentTime + " receive " + bytesRead;
							writeToFile(record);
							
							debugStatus = (int)totalBytesReceived + "";
							
							if (isStop)
							{
								break;
							}
						}
					}
					catch (Exception e)
					{
						//Log.e("exception", e.getMessage());
						debugStatus = "receiveFail";
						
						currentTime = System.currentTimeMillis();
						writeToFile(currentTime + " receiveFail 0");
						success = false;
					}
					if (!success)
					{
						try
						{
							iStream.close();
						}
						catch (Exception e)
						{
							
						}
					}
				}
			}
	    }	    
	}
	*/	    
}
