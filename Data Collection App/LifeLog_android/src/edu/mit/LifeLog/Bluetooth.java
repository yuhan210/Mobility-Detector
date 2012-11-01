package edu.mit.LifeLog;

import java.util.TimerTask;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Handler;

public class Bluetooth implements Sensor 
{
	private Logger logger;
	private Context context;
	private boolean isEnabled;
	private int scanIntervalInSec;
	private SensorType type;
	private String debugStatus;
	private Handler bluetoothHandler;
	private static int curGroundTruth;
	
	private int originalState; // stores the original bluetooth state and restore it after each scan
	
	public Bluetooth(Context context, Logger logger)
	{
		this.context = context;
		this.logger = logger;
		//this.type = SensorType.Bluetooth;
		this.isEnabled = false;
		this.scanIntervalInSec = 0;
		this.debugStatus = "no status";
		this.bluetoothHandler = new Handler();
		this.originalState = -1;
		
        // default setting
        changeSettings(type + FieldDelimiter + "1" + FieldDelimiter + "10");
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
			throw new RuntimeException("wrong setting string for bluetooth: " + settings);
		
		// cancel the current scanning 
		bluetoothHandler.removeCallbacks(bluetoothTask);
		
		this.isEnabled = (splitted[1].equals("1"));
		this.scanIntervalInSec = Integer.parseInt(splitted[2]);
		System.out.println("change bluetooth settings to: (" + isEnabled + ", " + scanIntervalInSec + ")");
		if (isEnabled)
			bluetoothHandler.postDelayed(bluetoothTask, 0);
		else
			logger.flushFile(type);
	}
	
	static int num = 0;
	private TimerTask bluetoothTask = new TimerTask()
	{		
		@Override
		public void run() 
		{
			originalState = BluetoothAdapter.getDefaultAdapter().getState();
			BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
			if (originalState != BluetoothAdapter.STATE_ON)
			{				
				context.registerReceiver(stateReceiver, new IntentFilter(BluetoothAdapter.ACTION_STATE_CHANGED));
				adapter.enable();			
			}
			else // already on
				doBluetoothScan();						
		}
		
		private BroadcastReceiver stateReceiver = new BroadcastReceiver()
		{
			@Override
			public void onReceive(Context c, Intent intent) 
			{
				int currentState = intent.getExtras().getInt(BluetoothAdapter.EXTRA_STATE);
				
				System.out.println("bluetooth status changed to : " + currentState);
				if (currentState == BluetoothAdapter.STATE_ON)			
					doBluetoothScan();		
			}		
		};
		
		private void doBluetoothScan()
		{
			context.registerReceiver(bluetoothReceiver, new IntentFilter(BluetoothDevice.ACTION_FOUND));
			context.registerReceiver(bluetoothReceiver, new IntentFilter(BluetoothAdapter.ACTION_DISCOVERY_FINISHED));
			 
			boolean r = BluetoothAdapter.getDefaultAdapter().startDiscovery();
			System.out.println("discover: " + r);
		}
		
		private BroadcastReceiver bluetoothReceiver = new BroadcastReceiver()
		{
			@Override
		    public void onReceive(Context context, Intent intent) 
			{			
		        String action = intent.getAction();
		        String timestamp = System.currentTimeMillis() + "";
		        
		        if (BluetoothDevice.ACTION_FOUND.equals(action)) 
		        {
		            // Get the BluetoothDevice object from the Intent
		            BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);

		            String record = device.getName() + PayloadFieldDelimiter + device.getAddress() + PayloadFieldDelimiter + curGroundTruth;
		            
		            // debug
		            //record += " " + num + " " + LifeLogService.getReadableCurrentTime();
		            
		            logger.writeRecord(type, timestamp, record);
		            System.out.println("bluetooth device: " + record);   
		        }
		        else if (BluetoothAdapter.ACTION_DISCOVERY_FINISHED.equals(action))
		        {		        
		        	System.out.println("BT discovery done");
				
		        	context.unregisterReceiver(bluetoothReceiver);
		        	if (originalState != BluetoothAdapter.STATE_ON)
		        		context.unregisterReceiver(stateReceiver);

		        	if (originalState == BluetoothAdapter.STATE_OFF || 
		        			originalState == BluetoothAdapter.STATE_TURNING_OFF)
		        		BluetoothAdapter.getDefaultAdapter().disable();		
					
		        	++num;
		        	
		        	debugStatus = LifeLogService.getReadableCurrentTime();
		        	if (isEnabled)		        	
		        		bluetoothHandler.postDelayed(bluetoothTask, scanIntervalInSec * 1000);

		        		
		        }
		        	
		    }
		};		
	};

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
		bluetoothHandler.removeCallbacks(bluetoothTask);
		
		logger.flushFile(type);
		
    	if (originalState == BluetoothAdapter.STATE_OFF || originalState == BluetoothAdapter.STATE_TURNING_OFF)
    		BluetoothAdapter.getDefaultAdapter().disable();		
	}

	@Override
	public String getDebugStatus() 
	{
		return type + FieldDelimiter + debugStatus;
	}

}
