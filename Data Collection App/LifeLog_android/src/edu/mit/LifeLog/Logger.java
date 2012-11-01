package edu.mit.LifeLog;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;
import java.text.SimpleDateFormat;
import java.util.Collection;
import java.util.Date;
import java.util.HashMap;
import java.util.Random;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

import edu.mit.LifeLog.Sensor.SensorType;

public class Logger 
{
	class SensorLogFile
	{
		private String filename;
		private BufferedWriter writer;
		
		SensorLogFile(String filename)
		{
			this.filename = filename;
			openWriter();
		}
		
		void openWriter()
		{
			try { this.writer = new BufferedWriter(new FileWriter(new File(filename)), 10000); }
			catch (IOException e) { throw new RuntimeException(e); }
		}
		
		void closeWriter() 
		{ 
			try { writer.close(); } 
			catch (IOException e) { throw new RuntimeException(e); }  
		}
		
		String getFilename() { return filename; }
		Writer getWriter() { return writer; }
	}
	
	private HashMap<SensorType, SensorLogFile> files;
	private Lock filesReadLock;
	private Lock filesWriteLock;
	private String phoneId;
	private Random random;
	
	public Logger(String rootDirectoryName, String filenamePrefix, String phoneId)
	{
		this.files = new HashMap<SensorType, SensorLogFile>();
		this.phoneId = phoneId;
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd-HH-mm-ss");        
        String currentTime = dateFormat.format(new Date());
        System.out.println("start now: " + currentTime);
        this.random = new Random();
		
        //try
        {
        	SensorType [] sensors = SensorType.values();
        	for (SensorType s : sensors)
        	{
        		//BufferedWriter w = new BufferedWriter(new FileWriter(rootDirectoryName + s + currentTime), 10000);
        		//files.put(s, w);
        		SensorLogFile f = new SensorLogFile(rootDirectoryName + s + currentTime);
        		files.put(s, f);
			}
        }
        //catch (IOException e) { throw new RuntimeException(e); }
        
        ReentrantReadWriteLock l = new ReentrantReadWriteLock();
        this.filesReadLock = l.readLock();
        this.filesWriteLock = l.writeLock();
	}

	/**
	 * Write a sensor record to file, the format is 
	 * <phone id> <FD> <time> <FD> <sensor name> <FD> <payload>, where FD = Sensor.FieldDelimiter
	 * @param sensorType type of sensor
	 * @param timestamp string representation of record timestamp
	 * @param payload payload
	 */
	public void writeRecord(SensorType sensorType, String timestamp, String payload)
	{		
		filesReadLock.lock();
		SensorLogFile w = files.get(sensorType);
		if (w == null)
			throw new RuntimeException("cannot find log file for sensor " + sensorType);
				
		int timestampPatch = random.nextInt(10000);
		try { w.getWriter().write(phoneId + Sensor.FieldDelimiter + timestamp + "." + timestampPatch + Sensor.FieldDelimiter + 
				                  sensorType + Sensor.FieldDelimiter + payload + "\n"); } 
		catch (IOException e) { throw new RuntimeException(e); }	
		filesReadLock.unlock();
	}
	
	/*
	public void flushAllFiles()
	{
		System.out.println("flush all logs");
		Collection<BufferedWriter> writers = files.values();
		try
		{
			for (BufferedWriter w : writers)
				w.flush();
		}
		catch (IOException e) { throw new RuntimeException(e); }		
	}
	*/
	
	public void flushFile(SensorType sensorType)
	{
		filesReadLock.lock();
		SensorLogFile w = files.get(sensorType);
		if (w == null)
			throw new RuntimeException("cannot find log file for sensor " + sensorType);
		
		System.out.println("flush log for: " + sensorType);
		try { w.getWriter().flush(); } 
		catch (IOException e) { throw new RuntimeException(e); }
		filesReadLock.unlock();
	}
	
	public void prepareForUpload()
	{
		File dataDir = new File(LifeLogService.DataDir);	
		// open the staging directory, creating it if not exists
    	File dataStagingDir = new File(LifeLogService.DataStagingDir); 
    	dataStagingDir.mkdir(); 
        
		filesWriteLock.lock();
		System.out.println("preparing logs for upload");
		
		Collection<SensorLogFile> writers = files.values();
		for (SensorLogFile w : writers)
			w.closeWriter();
		
		boolean success = dataDir.renameTo(dataStagingDir);
		System.out.println("rename success: " + success);
		
		// re-create the data directory and reopen the log files
		boolean r = new File(LifeLogService.DataDir).mkdir();
		System.out.println("mkdir success: " + r);
		
		for (SensorLogFile w : writers)
			w.openWriter();
		
		filesWriteLock.unlock();
	}
	

	public void shutdown()
	{
		filesReadLock.lock();
		System.out.println("close all logs");
		Collection<SensorLogFile> writers = files.values();
		try
		{
			for (SensorLogFile w : writers)
				w.getWriter().close();
		}
		catch (IOException e) { throw new RuntimeException(e); }
		filesReadLock.unlock();
	}
}
