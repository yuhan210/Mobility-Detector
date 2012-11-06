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
public class gsmTraining {

	public static final String[] activity = {"static","walking","running","biking","driving"};
	public static final int[] gt = {0,1,2,3,4};

	public static int TIMEWINDOW_INTERVAL = 60 * 1000; //ms
	public static int WINDOW_SIZE = 5;// number 
	public static int SHIFT_INTERVAL = 10 * 1000; //ms

	public static int[] samplingIntervalOption = {1};
	public static int samplingIntervalIndex = 0;


	public static String[] trainFileNames;
	public static String[] testFileNames;
	public static FileWriter[] fileWriterTrainArr;
	public static BufferedWriter[] bufWriterTrainArr;
	public static FileWriter[] fileWriterTestArr;
	public static BufferedWriter[] bufWriterTestArr;

	//public static final String PATHTORAWDATA = "C:\\Users\\yuhan\\Dropbox\\CITA_DATA";
	public static final String PATHTORAWDATA = "C:\\Users\\yuhan\\Dropbox\\test";
	public static void main(String args[]){

		try{

			// init feature output files //
			int samplingIntervalOptionNum = samplingIntervalOption.length;
			trainFileNames = new String[samplingIntervalOptionNum];
			fileWriterTrainArr = new FileWriter[samplingIntervalOptionNum];
			bufWriterTrainArr = new BufferedWriter[samplingIntervalOptionNum];

			testFileNames = new String[samplingIntervalOptionNum];
			fileWriterTestArr = new FileWriter[samplingIntervalOptionNum];
			bufWriterTestArr = new BufferedWriter[samplingIntervalOptionNum];
			for(int i = 0; i < samplingIntervalOptionNum ; ++i){
				trainFileNames[i] = "train_" + samplingIntervalOption[i];
				testFileNames[i] = "test_" + samplingIntervalOption[i];
				fileWriterTrainArr[i] = new FileWriter(trainFileNames[i]);
				fileWriterTestArr[i] = new FileWriter(testFileNames[i]);
				bufWriterTrainArr[i] = new BufferedWriter(fileWriterTrainArr[i]);
				bufWriterTestArr[i] = new BufferedWriter(fileWriterTestArr[i]);
			}
			// end of init//

			for(samplingIntervalIndex = 0; samplingIntervalIndex < samplingIntervalOption.length; ++samplingIntervalIndex){

				System.err.println("++++++ sampling interval: " + samplingIntervalOption[samplingIntervalIndex] + " sec(s) ++++++");
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

						for(int sensorIndex = 0; sensorIndex < sensorFileList.length; ++sensorIndex){ // find GPS file in a trace

							if(sensorFileList[sensorIndex].getName().indexOf("GSM") == 0){
								String inFileName = tracePath + "/" + sensorFileList[sensorIndex].getName();
								FileInputStream fstream = new FileInputStream(inFileName);
								DataInputStream in = new DataInputStream(fstream);
								BufferedReader br = new BufferedReader (new InputStreamReader(in));
								String strLine;
								int prevGroundTruth = -1;
								int counter = 0;

								CellList[] cellList = new CellList[15000];
								while((strLine = br.readLine())!= null){
									String header[] = strLine.split(",");
									String payload[] = strLine.split("\\|");

									if(prevGroundTruth != groundTruth && Integer.parseInt(payload[5]) == groundTruth){ // transition detected
										counter = 0;
										long timeStamp = Long.parseLong(header[1].substring(0,13));
										cellList[counter++] = new CellList(timeStamp,strLine);

										// Read all the scans with the correct gt
										while((strLine = br.readLine())!= null){
											String innerHeader[] = strLine.split(",");
											String innerPayload[] = strLine.split("\\|");

											if(Integer.parseInt(innerPayload[5]) == groundTruth){
												timeStamp = Long.parseLong(innerHeader[1].substring(0,13));
												cellList[counter++] = new CellList(timeStamp, strLine);

											}else{// stop
												processCellList(cellList, counter, groundTruth);
												initCellList(cellList);
												prevGroundTruth = Integer.parseInt(innerPayload[5]);
												break;
											}
										}
										if(strLine == null){
											processCellList(cellList, counter, groundTruth);	
										}

									}else{
										prevGroundTruth = Integer.parseInt(payload[5]);
									}

								}//end of while
								in.close();

							}// end of finding GPS file

						}

					}

				}	

				//
			}
			for(int i = 0; i < samplingIntervalOptionNum ; ++i){
				bufWriterTrainArr[i].close();
				bufWriterTestArr[i].close();
			}
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
	public static void processCellList(CellList[] rawCellList, int N, int groundTruth){

		//downsampling... l would be the downsampled cell list, and n is it's size.
		CellList l[] = new CellList[N];
		int downSamplingCounter = 0;
		l[downSamplingCounter++] = rawCellList[0];
		int prevIndex = 0;
		int n;
		for(int i = 1 ; i < N; ++i){

			int downsampleIndex = i;
			if((rawCellList[i].timeStamp - rawCellList[prevIndex].timeStamp) > (samplingIntervalOption[samplingIntervalIndex] * 1000)){
				long targetTime = rawCellList[prevIndex].timeStamp + samplingIntervalOption[samplingIntervalIndex] * 1000;
				if(Math.abs(rawCellList[i].timeStamp - targetTime) > Math.abs(rawCellList[i-1].timeStamp - targetTime)){
					if( (i-1) != prevIndex){
						downsampleIndex = (i-1);
					}
				}

				l[downSamplingCounter++] = rawCellList[downsampleIndex];		
				prevIndex = downsampleIndex;
			}

		}
		n = downSamplingCounter;
		// done



		int firstRawDataInCurrentWindow = 0;
		for(int i = 1; i < n; ++i){
			if( l[i].timeStamp - l[firstRawDataInCurrentWindow].timeStamp > TIMEWINDOW_INTERVAL){

				/** windowing... **/
				/** 
				  CellList currentCellList[] = new CellList[i - firstRawDataInCurrentWindow];
				  int counter = 0;
				  for(int j = firstRawDataInCurrentWindow; j < i ; ++j){
				  if((j - firstRawDataInCurrentWindow) >= (WINDOW_SIZE - 1)){
				  CellList cellWindow[] = new CellList[WINDOW_SIZE];
				  for(int k = 0; k < WINDOW_SIZE; ++k){
				  cellWindow[k] = l[j - (WINDOW_SIZE - 1) + k];
				  }
				  CellList windowCL = new CellList();
				  windowCL = generateWindowCellList(cellWindow);
				  if(windowCL.gsmList.size() > 0){
				  currentCellList[counter++] = windowCL;

				  }
				  }
				  }
				  int totalNumInWindow  = counter;
				 **/
				//

				CellList currentCellList[] = new CellList[i - firstRawDataInCurrentWindow];
				int counter = 0;
				for(int j = firstRawDataInCurrentWindow; j < i; ++j){
					//System.out.println(l[j]);
					currentCellList[counter++] = l[j];	
				}
				int totalNumInWindow  = counter;


				/* extract features */
				/* Feature 1: average common number of cell towers */
				/* Feature 2: average rssi difference */
				double aveCommonCellNumberRatio = 0.0;
				double aveRssiDifference = 0.0;
				double aveTanimotoDistance = 0.0;
				if(totalNumInWindow > 1){
					for(int j = 1; j < totalNumInWindow; ++j){
						
						int unionNum = unionCellNum(currentCellList[j-1], currentCellList[j]);	
						if(unionNum == 0){
							aveCommonCellNumberRatio += 0;
						}else{
							aveCommonCellNumberRatio += (sameCellnum(currentCellList[j-1], currentCellList[j])/ (double) unionNum);	
						}
						aveTanimotoDistance += TanimotoDistance(currentCellList[j-1], currentCellList[j]);

						aveRssiDifference += calDistance(currentCellList[j-1], currentCellList[j])/(double) unionNum;
					}
					aveCommonCellNumberRatio /= (totalNumInWindow - 1) * 1.0;
					aveRssiDifference /= (totalNumInWindow - 1) * 1.0;
					aveTanimotoDistance /= (totalNumInWindow - 1) * 1.0;
				}	

				/* Feature 4: Tanimoto difference between the 1st and last fingerprint in the time window */
				double firstLastDifference = TanimotoDistance(currentCellList[0] , currentCellList[totalNumInWindow-1]);


				try{

					Random r = new Random();
					String outFeature = aveCommonCellNumberRatio +","+ aveRssiDifference + ","+ aveTanimotoDistance + "," + firstLastDifference + "," + groundTruth+"\n";
					//System.out.println(outFeature);
					if(r.nextInt() > 0.5){//training feature
						bufWriterTrainArr[samplingIntervalIndex].write(outFeature);
					}else{ //test feature
						bufWriterTestArr[samplingIntervalIndex].write(outFeature);
					}


				}catch(Exception e){
					System.err.println("ERROR: "+ e.getMessage() + " "+ e);	
				}

				for(int j = firstRawDataInCurrentWindow; j < i; ++j){
					if((l[j].timeStamp - l[firstRawDataInCurrentWindow].timeStamp) >= SHIFT_INTERVAL){
						firstRawDataInCurrentWindow = j;			
						break;
					}
				}

			}

		}
	}


	public static CellList generateWindowCellList(CellList[] a){
		int TRUSTOCCURENCE = 3;
		double[][] cellIDList = new double[65536][2];
		double time = 0;
		for(CellList cellList: a){
			//System.out.println(cellList);
			time+= cellList.timeStamp;
			for(int i = 0; i < cellList.gsmList.size(); ++i){

				Cell cell =  cellList.gsmList.get(i);//for each cell

				++cellIDList[cell.cellId][0]; // number
				cellIDList[cell.cellId][1] += cell.rssi; // total rssi
			}
		}
		long time_long = (long)Math.round(time/WINDOW_SIZE);
		List<Cell> l = new ArrayList<Cell>();

		for(int i = 0; i < 65536; ++i){
			if(cellIDList[i][0] > TRUSTOCCURENCE){ // take this into account
				Cell c = new Cell(i, cellIDList[i][1]/cellIDList[i][0]);
				l.add(c);
			}
		}



		CellList result = new CellList(time_long,l);
		//System.out.println("---" + result);

		return result;

	}
	public static void initCellList(CellList[] l){
		for(int i = 0; i < l.length; ++i){
			l[i] = null;
		}
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
	public static double TanimotoDistance(CellList a, CellList b){
		
		double aLength = 0.0;
		double bLength = 0.0;
		double dotValue = 0.0;
		for(int i = 0; i < a.gsmList.size(); ++i){
			aLength += a.gsmList.get(i).rssi * a.gsmList.get(i).rssi; 

			for(int j = 0; j < b.gsmList.size(); ++j){
				
				bLength += b.gsmList.get(j).rssi * b.gsmList.get(j).rssi;

				if(a.gsmList.get(i).cellId == b.gsmList.get(j).cellId){
					dotValue += a.gsmList.get(i).rssi * b.gsmList.get(j).rssi;	
				}
			}
		}
		
		return dotValue == 0 ? 0 : (dotValue/(aLength + bLength - dotValue));
	}



	public static double calDistance(CellList a, CellList b){


		boolean aFound[] = new boolean[a.gsmList.size()];
		boolean bFound[] = new boolean[b.gsmList.size()];
		int counter = 0;
		double distance = 0;
		for(int i = 0; i < a.gsmList.size(); ++i){
			for(int j = 0; j < b.gsmList.size(); ++j){

				if(a.gsmList.get(i).cellId == b.gsmList.get(j).cellId){

					aFound[i] = true;
					bFound[j] = true;
					distance+= Math.pow((a.gsmList.get(i).rssi - b.gsmList.get(j).rssi),2);
					++counter;
					break;
				}
			}
		}
		for(int i = 0; i < a.gsmList.size(); ++i){
			if(aFound[i] == false){
				distance+= Math.pow(a.gsmList.get(i).rssi,2);
			}
		}
		for(int j = 0; j < b.gsmList.size(); ++j){
			if(bFound[j] == false){
				distance+= Math.pow(b.gsmList.get(j).rssi,2);
			}
		}

		return Math.sqrt(distance);
	}
	public static double calDistanceCTrack(CellList a, CellList b){


		boolean aFound[] = new boolean[a.gsmList.size()];
		boolean bFound[] = new boolean[b.gsmList.size()];
		int counter = 0;
		double distance = 0;
		for(int i = 0; i < a.gsmList.size(); ++i){

			for(int j = 0; j < b.gsmList.size(); ++j){

				if(a.gsmList.get(i).cellId == b.gsmList.get(j).cellId){

					aFound[i] = true;
					bFound[j] = true;
					distance+= Math.pow((a.gsmList.get(i).rssi - b.gsmList.get(j).rssi),2);
					++counter;
					break;
				}
			}
		}


		return Math.sqrt(distance);
	}
	public static int sameCellnum(CellList a, CellList b){


		int counter = 0;
		for(int i = 0; i < a.gsmList.size(); ++i){

			for(int j = 0; j < b.gsmList.size(); ++j){


				if(a.gsmList.get(i).cellId == b.gsmList.get(j).cellId){
					++counter;
					break;
				}
			}

		}

		return counter;
	}
	public static int unionCellNum(CellList a, CellList b){
		int intersect = sameCellnum(a, b);
		return (a.gsmList.size()+b.gsmList.size()-intersect);
	}
}


class CellList{
	List<Cell> gsmList;
	long timeStamp;   

	public CellList(){
		gsmList = new ArrayList<Cell>();
	}


	public CellList(long time, String s){

		this.gsmList = new ArrayList<Cell>();
		this.timeStamp = time;
		String segLine[] = s.split("\\|");
		String header[] = segLine[0].split(",");

		//355066049626536,1330620689656.2117,GSM,22187|6011|13|2|0|1|5|21511|11|22181|12|20352|9|22673|9|20353|6
		//cid|lac|rssi|networktype|datastate|gt| num| cid|rssi
		//22187|6011|13|2|0|1|5|21511|11|22181|12|20352|9|22673|9|20353|6

		Cell servingCell = new Cell(Integer.parseInt(header[3]), Double.parseDouble(segLine[2]));
		if(servingCell.isValid()){
			this.gsmList.add(servingCell);
		}
		int cellNum = Integer.parseInt(segLine[6]);
		if(segLine.length == cellNum * 3 + 7){ // if it has LAC
			for(int i = 0; i < cellNum;++i){
				Cell oneCell = new Cell(Integer.parseInt(segLine[7+ i*3]), Double.parseDouble(segLine[7 + i*3 + 2]));
				if(oneCell.isValid()){
					this.gsmList.add(oneCell);
				}
			}

		}else if(segLine.length == cellNum * 2+ 7){
			for(int i = 0; i < cellNum; ++i){
				Cell oneCell = new Cell(Integer.parseInt(segLine[7+i*2]),Double.parseDouble(segLine[7+i*2+1]));
				if(oneCell.isValid()){
					this.gsmList.add(oneCell);
				}
			}	
		}



	}
	public CellList(long time, List<Cell> l){
		this.timeStamp = time;
		this.gsmList = l;
	}
	public String toString(){

		DecimalFormat df = new DecimalFormat("#############");
		String result = df.format(timeStamp) + "," + gsmList.size() + ",";
		if(gsmList.size() > 0){
			for(int i = 0; i < gsmList.size(); ++i){
				result += gsmList.get(i).cellId +"s" +gsmList.get(i).rssi +"x"; 
			}
		}


		return result;
	}
	public String printCellList(){

		DecimalFormat df = new DecimalFormat("#############");
		String result = timeStamp + "," + gsmList.size() + ",";
		if(gsmList.size() > 0){
			for(int i = 0; i < gsmList.size(); ++i){
				result += gsmList.get(i).cellId +"s" +gsmList.get(i).rssi +"x"; 
			}
		}


		return result;
	}
	/**
	  public String printTrustCellList(){

//String result = timeStamp_int + "," + gsmList.size() + ",";
String result = timeStamp_int + ",";
String tmp = "";
int counter = 0;
for(int i = 0; i < gsmList.size(); ++i){
if(gsmList.get(i).rssi < 25){
++counter;
tmp += gsmList.get(i).cellId +"s" +gsmList.get(i).rssi +"x";
}
}
if(counter == 0){
return null;
}else{
result += counter + "," + tmp;
return result;
}

}**/		
}

class Cell{
	int cellId;
	double rssi;
	boolean valid;

	public Cell(int id, double rssi){

		if(id < 0 || rssi > 32){
			valid = false;
		}else{
			valid = true;
		}

		if(id > 65535){

			this.cellId = id & 0x0000ffff;

		}else{

			this.cellId = id;
		}

		this.rssi = rssi;
	}
	public void printCell(){
		System.out.println(cellId + " " + rssi + " "+ valid);
	}
	public boolean isValid(){
		return valid;
	}
}
