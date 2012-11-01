package edu.mit.LifeLog;

public interface Sensor 
{
	
	public SensorType getType();
	public void changeSettings(String settings);
	public String getSettingsString();
	public void stop();
	public String getDebugStatus();
	
	
	/**
	 * Delimiter for each field in the debug, settings, and log files
	 */
	static final String FieldDelimiter = ","; 
	/**
	 * Delimiter for starting a comment line in the settings and debug files 
	 */
	static final String CommentDelimiter = "#";
	/** 
	 * Delimiter for within the "payload" field in the log file	
	 */
	static final String PayloadFieldDelimiter = "|";
			
	static final String GPSName = "GPS";
	static final String WifiName = "Wifi";
	static final String GSMName = "GSM";
	static final String AcclName = "Accel";
	static final String CompassName = "Compass";
	static final String OrtName = "Orientation";
	static final String GyroName = "GYRO";
	static final String DownlinkName = "Wifi Band.";
	static final String NWLocName = "Geo Loc";
	static final String BrowserName = "Browser";
	static final String PhoneCallName = "Calls";
	static final String BluetoothName = "Bluetooth";
	static final String CameraName = "Camera";
	static final String SMSName = "SMS";
	static final String ProximityName = "Proximity";
	static final String LightName = "Light";
	static final String LogUploaderName = "Log Upload";	
	static final String LogServerLocatorName = "Log Server IP";
    static final String TouchName = "Touch screen";
	
	public enum TimeUnit
	{
		Minutes("m"),
		Seconds("s"),
		Milliseconds("ms"),
		Hertz("hz"),
		None("");
		
		private String desc;
		private TimeUnit(String desc) { this.desc = desc; }
		@Override public String toString() { return desc; }
	}
	
	public enum ScanSelectionType
	{
		Spinner, Text, None;
	}
	
	public enum SensorType
	{ 
		Wifi(WifiName, TimeUnit.Milliseconds, ScanSelectionType.Text),
		GPS(GPSName, TimeUnit.Milliseconds, ScanSelectionType.Text),
		GSM(GSMName, TimeUnit.Milliseconds, ScanSelectionType.Text),
		Accl(AcclName, TimeUnit.None, ScanSelectionType.Spinner),
		//Compass(CompassName, TimeUnit.None, ScanSelectionType.Spinner),
		Ort(OrtName, TimeUnit.None, ScanSelectionType.Spinner),
	//	TouchScreen(TouchName,TimeUnit.Milliseconds, ScanSelectionType.Text),
		Proximity(ProximityName, TimeUnit.None, ScanSelectionType.Spinner),
		Light(LightName, TimeUnit.None, ScanSelectionType.Spinner),
		//Downlink(DownlinkName, TimeUnit.Seconds, ScanSelectionType.Text),
		NWLoc(NWLocName, TimeUnit.Milliseconds, ScanSelectionType.Text),
		Browser(BrowserName, TimeUnit.Seconds, ScanSelectionType.Text),
		PhoneCall(PhoneCallName, TimeUnit.Seconds, ScanSelectionType.Text),
		GYRO(GyroName, TimeUnit.None, ScanSelectionType.Spinner);
	
		//Bluetooth(BluetoothName, TimeUnit.Seconds, ScanSelectionType.Text),
		//Camera(CameraName, TimeUnit.None, ScanSelectionType.None),
		//SMS(SMSName, TimeUnit.None, ScanSelectionType.None),
		//LogUploader(LogUploaderName, TimeUnit.Seconds, ScanSelectionType.Text),
	//	LogServerLocator(LogServerLocatorName, TimeUnit.None, ScanSelectionType.Text, false);
		
		private String name;
		private TimeUnit unit;
		private ScanSelectionType selectionType;
		private boolean hasToggleButton;
		
		private SensorType (String name, TimeUnit unit, ScanSelectionType selectionType, boolean hasToggleButton)
		{ this.name = name; this.unit = unit; this.selectionType = selectionType; this.hasToggleButton = hasToggleButton; }
		
		// default UI has toggle button
		private SensorType (String name, TimeUnit unit, ScanSelectionType selectionType) 
		{ this(name, unit, selectionType, true); }
		
		@Override public String toString() { return name; }
		public TimeUnit getUnit() { return unit; }
		public ScanSelectionType getSelectionType() { return selectionType; }
		public boolean hasToggleButton () { return hasToggleButton; }
		
		public static SensorType getSensorType(String name)
		{
			for (SensorType s : SensorType.values())
			{
				if (s.name.equals(name)) return s;
			}
			return null;			
		}
	}
}
