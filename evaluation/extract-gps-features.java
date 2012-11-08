import java.text.DecimalFormat;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.HashMap;
import java.util.Map;
import java.util.Iterator;
import java.util.Set;
import java.util.Arrays;
import org.gavaghan.geodesy.Ellipsoid;
import org.gavaghan.geodesy.GeodeticCalculator;
import org.gavaghan.geodesy.GeodeticCurve;
import org.gavaghan.geodesy.GeodeticMeasurement;
import org.gavaghan.geodesy.GlobalCoordinates;
import org.gavaghan.geodesy.GlobalPosition;


class extractGpsFeatures {

	public static final String[] activity = {"static","walking","running","biking","driving"};
	public static final int[] gt = {0,1,2,3,4};
	public static final int TIMEWINDOW_INTERVAL = 60 * 1000; //ms
	public static final int AVERAGE_SAMPLESIZE = 0;
	

	public static int[] samplingIntervalOption = {1,10};
	public static int samplingIntervalIndex = 0;

	public static String[] outFileNames;
	public static FileWriter[] fileWriterOutArr;
	public static BufferedWriter[] bufWriterOutArr;

	public static void main(String args[]){

		try{
			if ( args.length < 2 ) {
				System.out.println("Usage : java extractWifiTrain trace-file ground-truth");
				System.exit(-1);
			}

			// init feature output files //
			int samplingIntervalOptionNum = samplingIntervalOption.length;
			outFileNames = new String[samplingIntervalOptionNum];
			fileWriterOutArr = new FileWriter[samplingIntervalOptionNum];
			bufWriterOutArr = new BufferedWriter[samplingIntervalOptionNum];

			for(int i = 0; i < samplingIntervalOptionNum ; ++i){
				outFileNames[i] = "gps_" + samplingIntervalOption[i];
				fileWriterOutArr[i] = new FileWriter(outFileNames[i]);
				bufWriterOutArr[i] = new BufferedWriter(fileWriterOutArr[i]);
			}
			// end of init//

		for(samplingIntervalIndex = 0; samplingIntervalIndex < samplingIntervalOption.length; ++samplingIntervalIndex){
			String inFileName=args[0];
			System.out.println("in file is "+inFileName);
			int groundTruth=Integer.parseInt(args[1]);

			System.err.println("\n+++++++ sampling interval: " + samplingIntervalOption[samplingIntervalIndex] + "sec(s) +++++++");
							FileInputStream fstream = new FileInputStream(inFileName);
							DataInputStream in = new DataInputStream(fstream);
							BufferedReader br = new BufferedReader (new InputStreamReader(in));
							String strLine;
							int prevGroundTruth = -1;
							int counter = 0;

							location[] locList = new location[15000];
							while((strLine = br.readLine())!= null){
						     //354957034256753,1343956473110.2941,GPS,2|1343956473000|37.3739755153656|-121.99373245239258|-31.0|6.0|0.0|0.0|4						
							//phoneID, Time, GPS, GPSStatusCode|time|lat|lon|altitude| accuracy|speed| bearing |gt	
							String header[] = strLine.split(",");
							String payload[] = strLine.split("\\|");

							if(prevGroundTruth != groundTruth && Integer.parseInt(payload[8]) == groundTruth){ // transition detected
								counter = 0;
								long timeStamp = (Long.parseLong(header[1].substring(0,13))); //ms
								locList[counter++] = new location(timeStamp,strLine);

								// Read all the scans with the correct gt
								while((strLine = br.readLine())!= null){
									String innerHeader[] = strLine.split(",");
									String innerPayload[] = strLine.split("\\|");
									if(Integer.parseInt(innerPayload[8]) == groundTruth){
										timeStamp = (Long.parseLong(innerHeader[1].substring(0,13)));
										locList[counter++] = new location(timeStamp,strLine);

									}else{// stop
										processGPSList(locList, counter, groundTruth);
										initLocationList(locList);
										prevGroundTruth = Integer.parseInt(innerPayload[8]);
										break;
									}
								}
								if(strLine == null){
									processGPSList(locList, counter, groundTruth);	
								}

							}else{
								prevGroundTruth = Integer.parseInt(payload[8]);
							}

						}//end of while
						in.close();

		}// end of finding GPS file
		for(int i = 0; i < samplingIntervalOptionNum ; ++i){
				bufWriterOutArr[i].close();
		}
		}catch(Exception e)
		{
			System.err.println("ERROR: "+ e.getMessage() + " "+ e);
		}
	}
	public static void processGPSList(location[] rawGPSTrace, int NN, int groundTruth){
		//downsampling...
		location l[] = new location[NN];
		int downSamplingCounter = 0;
		l[downSamplingCounter++] = rawGPSTrace[0];
		int prevIndex = 0;
		for(int i = 1; i < NN; ++i){
			int downsampleIndex = i;
			if((rawGPSTrace[i].timeStamp - rawGPSTrace[prevIndex].timeStamp) > (samplingIntervalOption[samplingIntervalIndex] * 1000)){
				long targetTime = rawGPSTrace[prevIndex].timeStamp + samplingIntervalOption[samplingIntervalIndex] * 1000;
				if(Math.abs(rawGPSTrace[i].timeStamp - targetTime) > Math.abs(rawGPSTrace[i-1].timeStamp - targetTime)){
					if( (i-1) != prevIndex){
						downsampleIndex = (i-1);
					}
				}

				l[downSamplingCounter++] = rawGPSTrace[downsampleIndex];		
				prevIndex = downsampleIndex;
			}

		}
		int totalElement = downSamplingCounter;		
		// done, new trace in l, with size totalElement.	

		int firstRawDataInCurrentWindow = 0;

		for(int i = 1; i < totalElement; ++i){
			if(l[i].timeStamp - l[firstRawDataInCurrentWindow].timeStamp > TIMEWINDOW_INTERVAL){
				String outFeature = "";


				int windowElements = i-firstRawDataInCurrentWindow;
				location[] window = new location[windowElements];
				int counter = 0;
				for(int j = firstRawDataInCurrentWindow; j < i; ++j){
					window[counter++] = l[j];
				}

				/** Compute the features in the window **/
				int N = counter;
				if(N > 1){ // well...this ... might give us higher accuracy for sampling interval > 60sec/2

					/** Feature 1: Total distance of a segment **/
					double[] velocityArr = new double[N-1];
					int velocityCounter = 0;
					
					double currentWindowTotalDistance = 0.0;
					for(int j = 1; j < N ; ++j){

						currentWindowTotalDistance += calDistance(window[j-1],window[j]);
						velocityArr[velocityCounter++] = calSpeed(window[j-1], window[j]);

					}

					/** Feature 2: Expected velocity **/
					/** Feature 3: Maximum velocity **/
					double currentWindowExpectedVelocity = 0.0;
					double currentWindowMaxVelocity = 0.0;
					for(int j = 0; j < (N-1); ++j){
						currentWindowExpectedVelocity += velocityArr[j];
						if(velocityArr[j] > currentWindowMaxVelocity){
							currentWindowMaxVelocity = velocityArr[j];
						}
					}
					if(currentWindowExpectedVelocity > 0){
						currentWindowExpectedVelocity /= ((N-1)* 1.0);
					}

					outFeature += currentWindowTotalDistance + "," + currentWindowExpectedVelocity + "," + currentWindowMaxVelocity;

					/** Feature 4: Variance of velocity **/
					double currentWindowVar = 0.0;

					for(int j = 0; j < (N-1); ++j){
						currentWindowVar += (velocityArr[j] - currentWindowExpectedVelocity) * (velocityArr[j] - currentWindowExpectedVelocity);
					}
					if( currentWindowVar > 0 && (N-2) > 0){
						currentWindowVar /= (N-2) * 1.0;
					}

					outFeature += "," + currentWindowVar;

					/** Feature 5: Average Velocity **/
					double currentWindowAveVelocity = 0.0;
					if(currentWindowTotalDistance > 0 && (window[N-1].timeStamp - window[0].timeStamp) > 0){
						currentWindowAveVelocity = currentWindowTotalDistance / (double)((window[N-1].timeStamp - window[0].timeStamp)/1000.0) ;
					}
					outFeature += "," + currentWindowAveVelocity;
					try{
						if( !((groundTruth == 3 || groundTruth == 4) && currentWindowTotalDistance < 10)){
							Random r = new Random();
								bufWriterOutArr[samplingIntervalIndex].write(outFeature + "," + groundTruth +"\n");
						}
					}catch(Exception e){
						System.err.println("ERROR: "+ e.getMessage() + " "+ e);	

					}
				}
				firstRawDataInCurrentWindow += windowElements/6;

			}
		}
	}


	public static void initLocationList(location[] l){
		for(int i = 0; i < l.length; ++i){
			l[i] = null;
		}
	}
	public static double calDistance(location a, location b){
		GeodeticCalculator geoCalc = new GeodeticCalculator();
		// select a reference elllipsoid
		Ellipsoid reference = Ellipsoid.WGS84;

		// calculate the geodetic curve
		GeodeticCurve geoCurve = geoCalc.calculateGeodeticCurve(
				reference, new GlobalCoordinates(a.lat, a.lon), new GlobalCoordinates(b.lat, b.lon)
				);

		double ellipseMeters = geoCurve.getEllipsoidalDistance();
		return ellipseMeters;

	}
	public static double calDistance_simpleVersion(location a, location b){
		double theta = a.lon - b.lon;
		double dist = Math.sin(deg2rad(a.lat)) * Math.sin(deg2rad(b.lat)) + Math.cos(deg2rad(a.lat)) * Math.cos(deg2rad(b.lat)) * Math.cos(deg2rad(theta));
		dist = Math.acos(dist);
		dist = rad2deg(dist);
		dist = dist * 60 * 1.1515;
		dist = dist * 1.609344 * 1000;
		if(Double.isNaN(dist)){
			dist = 0;
		}
		return dist;
	}
	public static double calSpeed(location a, location b){

		double timeInterval = (Math.abs(b.timeStamp - a.timeStamp))/1000.0;
		double speed = 0.0;

		if(a.lat == b.lat && a.lon == b.lon ){
			speed = 0.0;
		}else{
			double distance = calDistance(a,b);
			if( distance == 0.0 || Double.isNaN(distance)){
				speed = 0.0;
			}else{	
				speed = distance/timeInterval;	
			}

		}
		return speed;

	}
	private static double deg2rad(double deg){
		return (deg * Math.PI / 180.0);
	}
	private static double rad2deg(double rad){
		return (rad * 180/ Math.PI);
	}
	public static double calMean(ArrayList<Double> l){
		double ave = 0;
		int count = 0;
		for(int i = 0; i < l.size(); ++i){
			if(l.get(i) > 0){
				ave *= count;
				ave += l.get(i);
				++count;
				ave/= (double) count;
			}
		}
		//double N = (double)l.size();
		//double mean = sum / N;
		return ave;

	}
	public static double calStd(ArrayList<Double> l, double m){

		double sum = 0;
		for(int i = 0; i < l.size(); ++i){
			if(l.get(i) > 0){
				sum += (l.get(i) - m) * (l.get(i) - m);
			}
		}
		sum /=(double)(l.size() - 1);
		return Math.sqrt(sum);

	}

}
class location{
	long timeStamp;
	double lat;
	double lon;
	double speed;
	double bearing; 

	public location(long time, String str){
		//354957034256753,1343956473110.2941,GPS,2|1343956473000|37.3739755153656|-121.99373245239258|-31.0|6.0|0.0|0.0|4					
		//phoneID, Time, GPS, GPSStatusCode|time|lat|lon|altitude| accuracy|speed| bearing |gt	

		this.timeStamp = time;
		String header[] = str.split(",");
		String payload[] = str.split("\\|");

		this.speed = Double.parseDouble(payload[6]);
		this.lat = Double.parseDouble(payload[2]);
		this.lon = Double.parseDouble(payload[3]);
		this.bearing = Double.parseDouble(payload[7]);
	}
	public location(long time, double lat, double lon, double speed, double bearing){
		this.lat = lat;
		this.lon = lon;
		this.speed = speed;
		this.bearing = bearing;
		this.timeStamp = time;
	}
}
