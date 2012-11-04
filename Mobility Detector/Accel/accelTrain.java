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
/**
 *  It searches for all the accel files in the ./static ./walking ./running ./biking ./driving folder.
 *  Compute the acceleration magnitude -> use a time window (it's size is specified in TIMEWINDOW_INTERVAL) -> extract various features from it 
 *  -> randomly write the features into two files ./train and ./test
 *
 **/

public class accelTrain {

	public static final int TIMEWINDOW_INTERVAL = 5 * 1000; //in ms, it decides the window size

	public static final String[] activity = {"static","walking","running","biking","driving"};
	public static final int[] gt = {0,1,2,3,4};

	public static FileWriter trainStream;
	public static BufferedWriter trainOut;
	public static FileWriter testStream;
	public static BufferedWriter testOut;

	public static final String PATHTORAWDATA = "C:\\Users\\yuhan\\Dropbox\\CITA_DATA";
	public static void main(String args[]){

		try{
			/***/
			trainStream = new FileWriter("train");
			trainOut = new BufferedWriter(trainStream);
			testStream = new FileWriter("test");
			testOut = new BufferedWriter(testStream);
			//



			File rawDataPath = new File(PATHTORAWDATA);
			File[] userDirList = rawDataPath.listFiles(); 
			for(int userIndex = 0; userIndex < userDirList.length; ++userIndex){// for each user's directory

				String userPath = PATHTORAWDATA + "/" + userDirList[userIndex].getName();
				File userDir = new File(userPath);
				File[] traceList = userDir.listFiles();
				for(int traceIndex = 0; traceIndex < traceList.length; ++traceIndex){// for each trace in a user's dir

					// check ground truth
					String tracePath = userPath + "/" + traceList[traceIndex].getName(); 
					int groundTruth = getGroundtruthFromFileName(traceList[traceIndex].getName());
					System.err.println(tracePath + ", " + activity[groundTruth]);
					if(groundTruth < 0){
						System.err.println("Trace:" + tracePath +", doesn't have a label.");
						System.exit(0);
					}
					//

					File traceDir =  new File(tracePath);
					File[] sensorFileList = traceDir.listFiles();

					for(int sensorIndex = 0; sensorIndex < sensorFileList.length; ++sensorIndex){ // find Accel file in a trace

						if(sensorFileList[sensorIndex].getName().indexOf("Accel") == 0){
							String inFileName = tracePath + "/" + sensorFileList[sensorIndex].getName();

							FileInputStream fstream = new FileInputStream(inFileName);
							DataInputStream in = new DataInputStream(fstream);
							BufferedReader br = new BufferedReader (new InputStreamReader(in));
							String strLine;

							int prevGroundTruth = -1;
							double lastTime = 0;
							int counter = 0;

							AccelElement accelList[] = new AccelElement[1000000];
							while((strLine = br.readLine())!= null){
								String header[] = strLine.split(",");
								String payload[] = header[3].split("\\|");

								if(prevGroundTruth != groundTruth && Integer.parseInt(payload[3]) == groundTruth){ // transition detected
									counter = 0;
									long timeStamp = Long.parseLong(header[1].substring(0,13));//in ms
									accelList[counter++] = new AccelElement(timeStamp, Double.parseDouble(payload[0])
											, Double.parseDouble(payload[1]), Double.parseDouble(payload[2]));

									// Read all the scans with the correct gt
									while((strLine = br.readLine())!= null){
										String innerHeader[] = strLine.split(",");
										String innerPayload[] = innerHeader[3].split("\\|");

										if(Integer.parseInt(innerPayload[3]) == groundTruth){
											timeStamp = Long.parseLong(innerHeader[1].substring(0,13));
											accelList[counter++] = new AccelElement(timeStamp, Double.parseDouble(innerPayload[0]), Double.parseDouble(innerPayload[1]), Double.parseDouble(innerPayload[2]));

										}else{// stop, we found a trace with the labelled groundtruth, extract feature
											processAccelList(accelList, counter, groundTruth); 
											initAccelList(accelList); // clean the array to find the next trace
											prevGroundTruth = Integer.parseInt(innerPayload[3]);
											break;
										}
									}
									if(strLine == null){ // found a trace
										processAccelList(accelList, counter, groundTruth);	
									}

								}else{
									prevGroundTruth = Integer.parseInt(payload[3]);
								}

							}//end of while
							in.close();

						}

					}

				}

			}	
			testOut.close();
			trainOut.close();

		}catch(Exception e)
		{
			System.err.println("ERROR: "+ e.getMessage() + " "+ e);
		}
	}
	public static int getGroundtruthFromFileName(String f){
		int i;
		for(i = 0; i < activity.length; ++i){
			if(f.indexOf(activity[i]) > 0){
				return gt[i];
			}
		}

		return -1;


	}

	public static void processAccelList(AccelElement[] a, int totalAccelElementNum, int groundTruth){
		
		int firstRawDataInCurrentWindow = 0;
		for(int i = 1; i < totalAccelElementNum; ++i){ // loop through the entire trace, totalAccelElementNum: number of samples in the trace 

			if(a[i].timeStamp - a[firstRawDataInCurrentWindow].timeStamp > TIMEWINDOW_INTERVAL){ // a timewindow
				String outFeature = "";
			
			        // process the time window, start time: a[firstRawDataInCurrentWindow].timeStamp, end time: a[i-1].timeStamp	
				int N = i-firstRawDataInCurrentWindow; //number of samples in the window
				AccelElement accelWindow[] = new AccelElement[N]; 		

				int counter = 0;
				for(int j = firstRawDataInCurrentWindow; j < i ; ++j){
					accelWindow[counter++] = a[j];
				}
				
				
				/** Calculating the features from the current window - accelWindow**/
				
				//**** Feature 1: Mean (time domain) ****//
				//**** Feature 2: Variance (time domain) ****//
				double currentWindowVar  = 0, currentWindowMean = 0;
				for(int k = 0; k < N; ++k){
					currentWindowMean += accelWindow[k].magnitude;
				}
				currentWindowMean /= (N * 1.0);
				for(int k = 0; k < N; ++k){
					currentWindowVar += (accelWindow[k].magnitude - currentWindowMean) * (accelWindow[k].magnitude - currentWindowMean); 
				}  
				currentWindowVar /= (double)(N-1);
				

				//**** Feature 3: Peak Power Frequency (freq domain) ****//
				double currentWindowFs = N/ ((accelWindow[N-1].timeStamp - accelWindow[0].timeStamp)/1000); // sampling frequency
				double currentWindowFFT[] = new double[((N/2) + 1)];   
				computeDFT(accelWindow, N, currentWindowFFT);
				
				// find peak power location
				double peakPower = -Double.MAX_VALUE;
				int peakPowerLocation = -1;
				for(int k = 1; k < currentWindowFFT.length; ++k){ // ignore index 0 (0Hz)
					if(currentWindowFFT[k] > peakPower){
						peakPower = currentWindowFFT[k];
						peakPowerLocation = k;
					}
				}
				double currentWindowPeakFreq = ((peakPowerLocation + 1)/(N* 1.0)) * currentWindowFs;
				
				//***** Feature 4: Peak Power Ratio (freq domain) ****//
				double sumPower = 0;
				int countPower = 0;
				for(int k = 1; k < currentWindowFFT.length; ++k){
					sumPower += currentWindowFFT[k];
					++countPower;
				}
				double currentWindowPeakPowerRatio = (peakPower * countPower)/sumPower;

				//***** Feature 5: Curve Length (time domain) *****//
				double currentWindowCL = 0.0;
				for(int k = 1; k < N; ++k){
					currentWindowCL += Math.abs(accelWindow[k].magnitude - accelWindow[k-1].magnitude);
				}

				//**** Feature 6: Non-linear Energy (time domain) ****//
				double currentWindowANE = 0.0;
				for(int k = 1; k < N-1; ++k){
					currentWindowANE += (accelWindow[k].magnitude * accelWindow[k].magnitude) - (accelWindow[k-1].magnitude * accelWindow[k+1].magnitude); 
				}
				currentWindowANE /= N * 1.0;

				//**** Feature 7: Window Energy (freq domain)****// 
				double currentWindowEnergy = 0.0;
				for(int k = 1; k < currentWindowFFT.length; ++k){
					currentWindowEnergy += currentWindowFFT[k];
				}

				//**** Feature 8: Strength Variation (time domain)****//
				List<Double> summit = new ArrayList<Double>();
				List<Double> valley = new ArrayList<Double>();
				for(int k = 1; k < N-1; ++k){
					if(accelWindow[k].magnitude > accelWindow[k-1].magnitude && accelWindow[k].magnitude > accelWindow[k+1].magnitude){
						summit.add(accelWindow[k].magnitude);

					}else if(accelWindow[k].magnitude < accelWindow[k-1].magnitude && accelWindow[k].magnitude < accelWindow[k+1].magnitude)
					{
						valley.add(accelWindow[k].magnitude);
					}
				}
				double summitVar = 0.0, valleyVar =0.0;
				double summitMean = 0.0, valleyMean = 0.0;
				for(int k = 0; k < summit.size(); ++k){
					summitMean += summit.get(k);
				}
				summitMean /= (double)summit.size();
				for(int k = 0; k < valley.size(); ++k){
					valleyMean += valley.get(k);
				}
				valleyMean /= (double)(valley.size());
				for(int k = 0; k < summit.size(); ++k){
					summitVar += (summit.get(k) - summitMean) * (summit.get(k) - summitMean);
				}
				if(summit.size() > 1){
					summitVar /= (double) (summit.size()-1);
				}else{
					summitVar = 0;
				}
				for(int k = 0; k < valley.size(); ++k){
					valleyVar += (valley.get(k) - valleyMean) * (valley.get(k) - valleyMean);
				}
				if(valley.size() > 1){
					valleyVar /= (double) (valley.size()-1);
				}else{
					valleyVar = 0;
				}
				double currentWindowSV = summitVar + valleyVar;


				//***** Feature 9: Entropy (freq-domain) *****//
				double currentWindowEntropy = 0;
				for(int k = 1; k < currentWindowFFT.length; ++k){
					double c = currentWindowFFT[k]/currentWindowEnergy;
					currentWindowEntropy += (c * Math.log(1/c));
				}
				

				outFeature += currentWindowMean + "," + currentWindowVar + "," + currentWindowPeakFreq +"," + 
				       currentWindowPeakPowerRatio+ "," + currentWindowCL + "," + currentWindowANE + "," + currentWindowEnergy + ","
				       + currentWindowSV + "," + currentWindowEntropy + "," + groundTruth;
				Random r = new Random();
				try{
					if(r.nextInt() > 0.5){
						trainOut.write(outFeature + "\n");
					}else{
						testOut.write(outFeature + "\n");
					}
				}catch(Exception e){
					System.err.println("ERROR: "+ e.getMessage() + " "+ e);
				}

				firstRawDataInCurrentWindow += N/2; // shift half of the window size
			}

		}


	}
	public static void computeDFT(AccelElement X[], int N, double Y[]) {

		for (int i = 0; i < (N/2 + 1); ++i) {
			double realPart = 0;
			double imgPart = 0;
			for (int j = 0; j < N; ++j) {
				realPart += (X[j].magnitude * Math.cos(-(2.0 * Math.PI * i * j)/N));
				imgPart +=  (X[j].magnitude * Math.sin(-(2.0 * Math.PI * i * j)/N));
			}
			realPart /= N;
			imgPart /= N;
			Y[i] = 2 * Math.sqrt(realPart * realPart + imgPart * imgPart);
		}
	}


	public static void initAccelList(AccelElement[] a){
		for(int i = 0; i < a.length; ++i){
			a[i] = null;
		}
	}

}



class AccelElement{
	double magnitude;
	long timeStamp;

	public AccelElement(long t, double x,double y,double z){

		this.magnitude = Math.sqrt(x *x + y*y + z*z);
		this.timeStamp = t;
	}
}
