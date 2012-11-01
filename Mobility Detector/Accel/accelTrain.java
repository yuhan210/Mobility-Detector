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

	public static final int TIMEWINDOW_INTERVAL = 5; //sec
	
	public static final String[] activity = {"static","walking","running","biking","driving"};
	public static final int[] gt = {0,1,2,3,4};
	public static final int accelFeatureNum = 6;
	public static final String root ="./";
	public static int actNum = 0;
	public static FileWriter trainStream;
	public static BufferedWriter trainOut;
	public static FileWriter testStream;
	public static BufferedWriter testOut;

	public static void main(String args[]){

		try{
			/***/
			trainStream = new FileWriter("train");
			trainOut = new BufferedWriter(trainStream);
			testStream = new FileWriter("test");
			testOut = new BufferedWriter(testStream);
			//
			//
			for(actNum = 0; actNum < activity.length; ++actNum){ // for each activity	
				System.out.println(activity[actNum]);


				File folder = new File(root + "/" + activity[actNum]);
				File[] listOfFiles = folder.listFiles(); 

				for (int f = 0; f < listOfFiles.length; ++f){

					if(listOfFiles[f].isFile() && listOfFiles[f].getName().indexOf(activity[actNum]) > 0){
						String fName = listOfFiles[f].getName();
						System.out.println(fName);

						String inFileName = root + "/" + activity[actNum] + "/" +fName;
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

							if(prevGroundTruth != gt[actNum] && Integer.parseInt(payload[3]) == gt[actNum]){ // transition detected
								counter = 0;
								double timeStamp = (Long.parseLong(header[1].substring(0,13))/1000);//in sec
								accelList[counter++] = new AccelElement(timeStamp, Double.parseDouble(payload[0])
										, Double.parseDouble(payload[1]), Double.parseDouble(payload[2]));

								// Read all the scans with the correct gt
								while((strLine = br.readLine())!= null){
									String innerHeader[] = strLine.split(",");
									String innerPayload[] = innerHeader[3].split("\\|");

									if(Integer.parseInt(innerPayload[3]) == gt[actNum]){
										timeStamp = (Long.parseLong(innerHeader[1].substring(0,13))/1000);
										accelList[counter++] = new AccelElement(timeStamp, Double.parseDouble(innerPayload[0])
												, Double.parseDouble(innerPayload[1]), Double.parseDouble(innerPayload[2]));

									}else{// stop
										processAccelList(accelList, counter);
										lastTime = accelList[counter - 1].timeStamp;		
										initAccelList(accelList);
										prevGroundTruth = Integer.parseInt(innerPayload[3]);
										break;
									}
								}
								if(strLine == null){
									processAccelList(accelList, counter);	
								}

							}else{
								prevGroundTruth = Integer.parseInt(payload[3]);
							}

						}//end of while
						in.close();
					}//end of if for correct files 
				}//end of for every file
			}// end of each activity
			testOut.close();
			trainOut.close();

		}catch(Exception e)
		{
			System.err.println("ERROR: "+ e.getMessage() + " "+ e);
		}
	}

	public static double calMean(ArrayList<Double> a){	
		double sum = 0.0;
		for(int i = 0; i < a.size(); ++i){
			sum  += a.get(i);
		}
		return sum/ (double)a.size();

	}
	public static double calStd(double m, ArrayList<Double> a){

		double tmp = 0.0;
		for(int i = 0; i < a.size(); ++i){
			tmp += (a.get(i) - m)*(a.get(i) - m);
		}
		tmp /= (double)(a.size()-1);

		return Math.sqrt(tmp);

	}

	public static void processAccelList(AccelElement[] a, int NN){
	int firstRawDataInCurrentWindow = 0;

		for(int j = 1; j < NN; ++j){

				if(a[j].timeStamp - a[firstRawDataInCurrentWindow].timeStamp >= TIMEWINDOW_INTERVAL){
					String outFeature = "";
					AccelElement accelWindow[] = new AccelElement[j-firstRawDataInCurrentWindow+1];		
					
					int counter = 0;
					for(int k = firstRawDataInCurrentWindow; k <= j ; ++k){
						accelWindow[counter++] = a[k];
					}

					/** Calculating the features **/

					int N = counter; // samples in the window
					//**** Feature 1: Variance ****//
					double mean = 0, currentWindowVar  = 0, currentWindowMean = 0;
					for(int k = 0; k < N; ++k){
						mean += accelWindow[k].magnitude;
					}
					mean /= (N * 1.0);
					for(int k = 0; k < N; ++k){
						currentWindowVar += (accelWindow[k].magnitude - mean) * (accelWindow[k].magnitude - mean); 
					}  
					currentWindowMean = mean;
					currentWindowVar /= (double)(N-1);
					outFeature = "" + currentWindowVar;

					//**** Feature 2: Peak Power Frequency (freq domain) ****//


					double currentWindowFs = N/ ((accelWindow[N-1].timeStamp - accelWindow[0].timeStamp)); // sampling frequency
					double currentWindowFFT[] = new double[((N/2) + 1)];   
					computeDFT(accelWindow, N, currentWindowFFT);
					// find peak power location
					double peakPower = -Double.MAX_VALUE;
					int peakPowerLocation = -1;
					for(int k = 1; k < currentWindowFFT.length; ++k){ // ignore index 0
						if(currentWindowFFT[k] > peakPower){
							peakPower = currentWindowFFT[k];
							peakPowerLocation = k;
						}
					}
					double currentWindowPeakFreq = ((peakPowerLocation + 1)/(N* 1.0)) * currentWindowFs;
					outFeature += "," + currentWindowPeakFreq;
					//***** Feature 3 Peak Power Ratio (freq domain) ****//
					double sumPower = 0;
					int countPower = 0;
					for(int k = 1; k < currentWindowFFT.length; ++k){
						sumPower += currentWindowFFT[k];
						++countPower;
					}
					double currentWindowPeakPowerRatio = (peakPower * countPower)/sumPower;
					outFeature += "," + currentWindowPeakPowerRatio;

					//***** Feature 4: Curve Length (time domain) *****//
					double currentWindowCL = 0.0;
					for(int k = 1; k < N; ++k){
						currentWindowCL += Math.abs(accelWindow[k-1].magnitude - accelWindow[k].magnitude);
					}
					outFeature += "," + currentWindowCL;

					//**** Feature 5: Non-linear Energy (time domain) ****//
					double currentWindowANE = 0.0;
					for(int k = 1; k < N-1; ++k){
						currentWindowANE += (accelWindow[k].magnitude * accelWindow[k].magnitude) - (accelWindow[k-1].magnitude * accelWindow[k+1].magnitude); 
					}
					currentWindowANE /= (double)N;
					outFeature += "," + currentWindowANE;

					//**** Feature 6: Window Energy ****// 

					double currentWindowEnergy = 0.0;
					for(int k = 1; k < currentWindowFFT.length; ++k){
						currentWindowEnergy += currentWindowFFT[k];
					}

					outFeature += "," + currentWindowEnergy;

					//**** Feature 7: Strength Variation ****//
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
					
					outFeature += "," + currentWindowSV;
					//***** Feature 8: Mean  *****//
					outFeature += "," + currentWindowMean;
	

					//***** Feature 9: Entropy (freq-domain) *****//
					double currentWindowEntropy = 0;
					for(int k = 1; k < currentWindowFFT.length; ++k){
						double c = currentWindowFFT[k]/currentWindowEnergy;
						currentWindowEntropy += (c * Math.log(1/c));
					}
					outFeature += "," + currentWindowEnergy;

					outFeature += "," + gt[actNum];
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

					firstRawDataInCurrentWindow += N/2;
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
	double timeStamp;

	public AccelElement(double t, double x,double y,double z){

		this.magnitude = Math.sqrt(x *x + y*y + z*z);
		this.timeStamp = t;
	}
}
