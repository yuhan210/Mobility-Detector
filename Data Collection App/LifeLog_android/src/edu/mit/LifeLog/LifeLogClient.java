package edu.mit.LifeLog;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.pm.PackageManager;
import android.graphics.Typeface;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Message;
import android.os.Messenger;
import android.os.RemoteException;
import android.text.InputType;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
//import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;
import android.widget.Toast;

import edu.mit.LifeLog.Sensor.SensorType;

public class LifeLogClient extends Activity
{
	private Messenger mService = null;
	private boolean mIsBound;
    private Handler printHandler;

	private HashMap<SensorType, SensorUI> sensorUIs;
	
	private final Messenger mMessenger = new Messenger(new IncomingHandler());
	
	private static final int DebugPrintInterval = 1000;

	/**
	 * Class for interacting with the main interface of the service.
	 */
	private ServiceConnection mConnection = new ServiceConnection() 
	{
		public void onServiceConnected(ComponentName className, IBinder service) 
		{
			// This is called when the connection with the service has been
			// established, giving us the service object we can use to
			// interact with the service.  We are communicating with our
			// service through an IDL interface, so get a client-side
			// representation of that from the raw service object.
			mService = new Messenger(service);
			System.out.println("attached");

			try 
			{
				Message msg = Message.obtain(null, LifeLogService.MSG_STATUS_QUERY, null);
				msg.replyTo = mMessenger;
				mService.send(msg);
				
			} catch (RemoteException e) {
				// In this case the service has crashed before we could even
				// do anything with it; we can count on soon being
				// disconnected (and then reconnected if it can be restarted)
				// so there is no need to do anything here.
			}
			
			Toast.makeText(LifeLogClient.this, "LifeLog service connected", Toast.LENGTH_SHORT).show();
		}

		public void onServiceDisconnected(ComponentName className) 
		{
			// This is called when the connection with the service has been
			// unexpectedly disconnected -- that is, its process crashed.
			mService = null;
			//mCallbackText.setText("Disconnected.");
			System.out.println("disconnected");
			Toast.makeText(LifeLogClient.this, "LifeLog service disconnected", Toast.LENGTH_SHORT).show();
		}
	};
	
	private boolean hasInitialized = false;
	
	@Override
    public void onCreate(Bundle savedInstanceState) 
    {	
	    super.onCreate(savedInstanceState);
	    
	    System.out.println("on create");
	    
	    if (hasInitialized) return;
	    
	    hasInitialized = true;
	    System.out.println("initialize");
	    
	    this.sensorUIs = new HashMap<SensorType, SensorUI>();
		
		
		LinearLayout layout = new LinearLayout(this);				
		layout.setOrientation(LinearLayout.VERTICAL);
		
		
		
		GroundTruthUI gtui = new GroundTruthUI(this,layout, this);
		
		/*
		TableLayout buttonsTable = new TableLayout(this);
		
		buttonsTable.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.FILL_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));		
		buttonsTable.setStretchAllColumns(true);
		
		TableRow buttonsRow = new TableRow(this);
		
	    Button startServiceButton = new Button(this);
	    startServiceButton.setText("start service");
	    startServiceButton.setOnClickListener(mStartListener);
	    buttonsRow.addView(startServiceButton);
	    
	    Button stopServiceButton = new Button(this);
	    stopServiceButton.setText("stop service");
	    stopServiceButton.setOnClickListener(mStopListener);
	    buttonsRow.addView(stopServiceButton);

	    buttonsTable.addView(buttonsRow);

	    
	    buttonsRow = new TableRow(this);
	    
	    Button bindButton = new Button(this);
	    bindButton.setText("bind service");
	    bindButton.setOnClickListener(mBindListener);
	    buttonsRow.addView(bindButton);
	    
	    Button unbindButton = new Button(this);
	    unbindButton.setText("unbind service");
	    unbindButton.setOnClickListener(mUnbindListener);
	    buttonsRow.addView(unbindButton);
	    
	    buttonsTable.addView(buttonsRow);
	    */						   
		
		ScrollView scrollView = new ScrollView(this);
		//scrollView.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.FILL_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
		TableRow.LayoutParams layoutParams = new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.MATCH_PARENT);
	//	layoutParams.span = 30;
		layoutParams.gravity = Gravity.CENTER_HORIZONTAL;
		
		
		
		
		TableLayout sensorTable = new TableLayout(this);
		sensorTable.setStretchAllColumns(true);
		sensorTable.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.FILL_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
		
		
		
		/////
		
		layoutParams = new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.FILL_PARENT);
		
		TableRow headerRow = new TableRow(this);
		TextView sensorHeader = new TextView(this);
		sensorHeader.setText("Sensor");
		sensorHeader.setGravity(Gravity.CENTER);
		sensorHeader.setTypeface(Typeface.defaultFromStyle(Typeface.ITALIC), Typeface.ITALIC);
		sensorHeader.setTextSize(TypedValue.COMPLEX_UNIT_SP, 10);
		sensorHeader.setFocusable(true);
		sensorHeader.setFocusableInTouchMode(true);
		sensorHeader.requestFocus();
				
		TextView enabledHeader = new TextView(this);
		enabledHeader.setText("Enabled?");
		enabledHeader.setGravity(Gravity.CENTER);
		enabledHeader.setTypeface(Typeface.defaultFromStyle(Typeface.ITALIC), Typeface.ITALIC);
		enabledHeader.setTextSize(TypedValue.COMPLEX_UNIT_SP, 10);
		
		TextView periodHeader = new TextView(this);
		periodHeader.setText("Freq");
		periodHeader.setGravity(Gravity.CENTER);
		periodHeader.setTypeface(Typeface.defaultFromStyle(Typeface.ITALIC), Typeface.ITALIC);
		periodHeader.setTextSize(TypedValue.COMPLEX_UNIT_SP, 10);
		
		TextView emptyHeader = new TextView(this);
		emptyHeader.setText("");
		emptyHeader.setGravity(Gravity.CENTER);
		emptyHeader.setTypeface(Typeface.defaultFromStyle(Typeface.ITALIC), Typeface.ITALIC);
		emptyHeader.setTextSize(TypedValue.COMPLEX_UNIT_SP, 10);
		
		TextView debugHeader = new TextView(this);
		debugHeader.setText("Debug Msg");
		debugHeader.setGravity(Gravity.CENTER);
		debugHeader.setTypeface(Typeface.defaultFromStyle(Typeface.ITALIC), Typeface.ITALIC);
		debugHeader.setTextSize(TypedValue.COMPLEX_UNIT_SP, 10);
		
		headerRow.addView(sensorHeader);
		headerRow.addView(enabledHeader);
		headerRow.addView(periodHeader);
		headerRow.addView(emptyHeader);
		headerRow.addView(debugHeader);
		
		sensorTable.addView(headerRow);
		
		// initialize the messengers		
		doStartService();
		doBindService();		
		
		SensorManager sensorManager = (SensorManager)getSystemService(Context.SENSOR_SERVICE);
		PackageManager pm = getPackageManager();
		
		for (SensorType type : SensorType.values())
		{
			TableRow sensorRow = new TableRow(this);
			
	        if (type == SensorType.GPS && !pm.hasSystemFeature(PackageManager.FEATURE_LOCATION_GPS))
	        { System.out.println("phone does not have GPS"); continue; }
	        else if (type == SensorType.Wifi && !pm.hasSystemFeature(PackageManager.FEATURE_WIFI))
	        { System.out.println("phone does not have wifi"); continue; }
	        else if (type == SensorType.GSM && !pm.hasSystemFeature(PackageManager.FEATURE_TELEPHONY_GSM))
	        { System.out.println("phone does not have GSM"); continue; }
	        else if (type == SensorType.NWLoc && !pm.hasSystemFeature(PackageManager.FEATURE_LOCATION_NETWORK))
			{ System.out.println("phone does not have geo location service"); continue; }
	        else if (type == SensorType.Accl && !pm.hasSystemFeature(PackageManager.FEATURE_SENSOR_ACCELEROMETER))	
	        { System.out.println("phone does not have accelerometer"); continue; }
	  //      else if (type == SensorType.Compass && !pm.hasSystemFeature(PackageManager.FEATURE_SENSOR_COMPASS))
	   //     { System.out.println("phone does not have compass"); continue; }
	        else if (type == SensorType.Ort && sensorManager.getSensorList(android.hardware.Sensor.TYPE_ORIENTATION).size() == 0)		
	        { System.out.println("phone does not have orientation sensor"); continue; }
	       // else if (type == SensorType.Bluetooth && !pm.hasSystemFeature(PackageManager.FEATURE_BLUETOOTH))
	       // { System.out.println("phone does not have bluetooth"); continue; }
	       // else if (type == SensorType.Camera && !pm.hasSystemFeature(PackageManager.FEATURE_CAMERA))	
	        //{ System.out.println("phone does not have camera"); continue; }
	       //else if (type == SensorType.Light && sensorManager.getSensorList(android.hardware.Sensor.TYPE_LIGHT).size() == 0)
	       //{ System.out.println("phone does not have light sensor"); continue; }
	        //else if (type == SensorType.Proximity && sensorManager.getSensorList(android.hardware.Sensor.TYPE_PROXIMITY).size() == 0)
	        //{ System.out.println("phone does not have proximity sensor"); continue; }
	        else if(type == SensorType.GYRO && sensorManager.getSensorList(android.hardware.Sensor.TYPE_GYROSCOPE).size() == 0)  
	        { System.out.println("phone does not have gyroscope sensor"); continue; }
	       
	        SensorUI ui = new SensorUI(type, this, sensorRow, layoutParams, this);
			sensorUIs.put(type, ui);
			
			sensorTable.addView(sensorRow);
		}
			
		layoutParams = new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.MATCH_PARENT);
		layoutParams.span = 5;
		layoutParams.gravity = Gravity.CENTER_HORIZONTAL;
		/*
		TableRow stopLogRow = new TableRow(this);
		
		Button stopLogSendingButton = new Button(this);
		stopLogSendingButton.setText("Stop Log Sending");
		stopLogSendingButton.setLayoutParams(layoutParams);
		stopLogRow.addView(stopLogSendingButton);
		*/
		/*
		CheckBox box = new CheckBox(this);
		box.setText("Send Logs to Server");
		box.setLayoutParams(layoutParams);
		box.setChecked(true);
		stopLogRow.addView(box);
		sensorTable.addView(stopLogRow);
		*/
		TableRow stopServiceRow = new TableRow(this);
	    Button stopServiceButton = new Button(this);
	    stopServiceButton.setText("Stop LifeLog Service");
	    stopServiceButton.setLayoutParams(layoutParams);
	    stopServiceButton.setOnClickListener(mStopListener);
	    stopServiceRow.addView(stopServiceButton);	 
	    
		TextView logUploadLabel = new TextView(this);
		logUploadLabel.setText("Log Server IP");		
		logUploadLabel.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16);
		logUploadLabel.setGravity(Gravity.LEFT);
		logUploadLabel.setLayoutParams(layoutParams);
	    
	    sensorTable.addView(stopServiceRow);
		scrollView.addView(sensorTable);	
				
		//layout.addView(buttonsTable);
		layout.addView(scrollView);
		
		
    	// set up the debug status handler
        this.printHandler = new Handler();
    	printHandler.postDelayed(printStatusTask, 0);
    	
		setContentView(layout);
    }
	
	/**
	 * Callback function for the SensorUIs to change sensor settings
	 */
	public void sendChangeSettingsMsg()
	{
		if (mService != null)
		{
			try
			{
				Message msg = Message.obtain(null, LifeLogService.MSG_CHANGE_SETTINGS, null);
				msg.replyTo = mMessenger;
				mService.send(msg);
			}
			catch (RemoteException e) { throw new RuntimeException("fail to send change settings msg"); }			
		}
		else
			Toast.makeText(LifeLogClient.this, "Can't connect to LifeLog service", Toast.LENGTH_SHORT).show();
	}
	
	@Override
	public void onPause()
	{
		super.onPause();
		System.out.println("on pause");		
	}
	
	@Override
	public void onDestroy()
	{
		super.onDestroy();
		doUnbindService();
		System.out.println("destroyed");
	}
		
	private OnClickListener mStopListener = new OnClickListener()
	{
		public void onClick(View v) { doUnbindService(); doStopService(); }
	};
		
	/*
	private OnClickListener mStartListener = new OnClickListener() 
	{
		public void onClick(View v) { doStartService(); }		
	};
	
	private OnClickListener mBindListener = new OnClickListener() 
	{
		public void onClick(View v) { doBindService(); }		
	};

	private OnClickListener mUnbindListener = new OnClickListener() 
	{
		public void onClick(View v) { doUnbindService(); }		
	};
	*/	
	
	private void doStartService() 
	{
		ComponentName n = startService(new Intent(LifeLogClient.this, LifeLogService.class));
		if (n != null)
			System.out.println("started: " + n);
		else
			System.out.println("null service returned");
		System.out.println("starting service");
	}
	
	private void doStopService()
	{
		boolean stopped = stopService(new Intent(LifeLogClient.this, LifeLogService.class));
		System.out.println("stopped service: " + stopped);
	}
	
	private void doBindService() 
	{
		// Establish a connection with the service.  We use an explicit
		// class name because there is no reason to be able to let other
		// applications replace our component.
		bindService(new Intent(LifeLogClient.this, LifeLogService.class), mConnection, Context.BIND_AUTO_CREATE);
		mIsBound = true;
		//mCallbackText.setText("Binding.");
		System.out.println("Binding");
	}

	void doUnbindService() 
	{
		if (mIsBound) 
		{
			// If we have received the service, and hence registered with
			// it, then now is the time to unregister.
			if (mService != null) 
			{
				/*
				try {
					Message msg = Message.obtain(null, SensorDataService.MSG_UNREGISTER_CLIENT);
					msg.replyTo = mMessenger;
					mService.send(msg);
				} catch (RemoteException e) {
					// There is nothing special we need to do if the service
					// has crashed.
				}
				*/
			}

			// Detach our existing connection.
			unbindService(mConnection);
			mIsBound = false;
			System.out.println("Unbinding");
		}
	}	
	
	class IncomingHandler extends Handler 
	{
		@Override
		public void handleMessage(Message msg) 
		{
			switch (msg.what) 
			{
			case LifeLogService.MSG_STATUS_QUERY:
				try
				{
					BufferedReader r = new BufferedReader(new FileReader(LifeLogService.ResponseFile), 1000);
					String line;
					while ((line = r.readLine()) != null)
					{
						System.out.println("Received from service: " + line);
						String [] splitted = line.split(Sensor.FieldDelimiter);
						SensorUI ui = sensorUIs.get(SensorType.getSensorType(splitted[0]));
						if (ui == null)
							throw new RuntimeException("cannot find UI for sensor: " + line);
						ui.changeUI(line);
					}
					r.close();
				}
				catch (IOException e) { throw new RuntimeException(e); }
								

				break;
			default:
				super.handleMessage(msg);
			}
		}
	}
	
	private Runnable printStatusTask = new Runnable() 
	{			
		public void run() 
		{					
			try
			{ 
				File f = new File(LifeLogService.DebugMsgFile);
				if (!f.exists()) 
				{ 
					printHandler.postDelayed(printStatusTask, DebugPrintInterval);	
					return; 
				}

				BufferedReader r = new BufferedReader(new FileReader(LifeLogService.DebugMsgFile), 10000);
				
				String line;
				while ((line = r.readLine()) != null)
				{					
					if (line.startsWith(Sensor.CommentDelimiter)) continue;
					String [] splitted = line.split(Sensor.FieldDelimiter);
					SensorUI ui = sensorUIs.get(SensorType.getSensorType(splitted[0]));
					if (ui == null)
					{
						System.out.println("cannot find debug status for sensor: " + splitted[0]);
						continue;
					}
															
					ui.changeDebugStatus(line);
				}				
				
				r.close();
			} 
			catch (IOException e) { throw new RuntimeException(e); }
						
			printHandler.postDelayed(printStatusTask, DebugPrintInterval);						
		}
	};
}
