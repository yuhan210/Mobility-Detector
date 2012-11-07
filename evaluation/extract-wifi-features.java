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
import java.lang.Integer;

/**
 *  Take the trace file name and interested ground truth as input and generate feature vectors. 
 **/
class extractWifiFeatures {

	public static final String[] activity = {"static","walking","running","biking","driving"};
	public static final int[] gt = {0,1,2,3,4};

	public static int TIMEWINDOW_INTERVAL = 60 * 1000; //ms
	public static int SHIFT_INTERVAL = 10 * 1000; //ms

	public static String[] outFileNames;
	public static FileWriter[] fileWriterOutArr;
	public static BufferedWriter[] bufWriterOutArr;

	public static int[] samplingIntervalOption = {1,10};
	public static int samplingIntervalIndex = 0;

	public static final String PATHTORAWDATA = "/tmp/CITA_DATA";	
//	public static final String PATHTORAWDATA = "C:\\Users\\yuhan\\Dropbox\\test";
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
				outFileNames[i] = "out_" + samplingIntervalOption[i];
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

								WiFiAPList[] wifiAPList = new WiFiAPList[15000];
								while((strLine = br.readLine())!= null){
									//356441045935745,1349407899513.1902,Wifi,3|MIT|00:21:d8:49:98:62|-85|5|1|MIT SECURE|00:26:cb:f4:13:03|-88|2437|TOPOFTHEHUB2|00:1a:70:fd:f0:49|-88|2442|MIT GUEST|00:21:d8:49:98:61|-87|2462|MIT|00:21:d8:49:98:62|-85|2462|MIT SECURE|00:26:cb:f4:14:03|-84|24123
									String header[] = strLine.split(",");
									String payload[] = strLine.split("\\|");

                                                                        try {
									    if(prevGroundTruth != groundTruth && Integer.parseInt(payload[5]) == groundTruth){ // transition detected
									    	counter = 0;
									    	long timeStamp = Long.parseLong(header[1].substring(0,13)); //ms
									    	wifiAPList[counter++] = new WiFiAPList(timeStamp,strLine);

									    	// Read all the scans with the correct gt
									    	while((strLine = br.readLine())!= null){
									    		String innerHeader[] = strLine.split(",");
									    		String innerPayload[] = strLine.split("\\|");

                                                                                               try {
                                                                                                   if(Integer.parseInt(innerPayload[5]) == groundTruth){
                                                                                               	timeStamp = Long.parseLong(innerHeader[1].substring(0,13));
                                                                                               	try  { 								
                                                                                                         wifiAPList[counter++] = new WiFiAPList(timeStamp, strLine);
                                                                                                       }
                                                                                                       catch (Exception e) {
                                                                                                         System.out.println("Array out of bounds .. continuing \n");
                                                                                                         continue;
                                                                                                       }
                                                                                                   }  
                                                                                                   else{// stop
                                                                                                     processAPList(wifiAPList, counter, groundTruth);
                                                                                               	 initAPList(wifiAPList);
                                                                                               	 prevGroundTruth = Integer.parseInt(innerPayload[5]);
                                                                                               	 break;
                                                                                                   }
                                                                                               }
                                                                                               catch (Exception e) {
                                                                                                    System.err.println("Exception in if, continuing .. \n");
                                                                                                    continue;
                                                                                               }
        								    		}
									    	if(strLine == null){
									    		processAPList(wifiAPList, counter, groundTruth);	
									    	}

									    }else{
									    	prevGroundTruth = Integer.parseInt(payload[5]);
									    }
                                                                        }
                                                                        catch (Exception e) {
                                                                             System.err.println("Yet another array out of bounds error, ignore \n");
                                                                             continue;
                                                                        }

								}//end of while
			}
			for(int i = 0; i < samplingIntervalOptionNum ; ++i){
				bufWriterOutArr[i].close();
			}

		}catch(Exception e)
		{
		   e.printStackTrace();	
                   System.err.println("ERROR: "+ e.getMessage() + " "+ e);
		}
	}

	public static void processAPList(WiFiAPList[] rawFPList, int N, int groundTruth){

		//downsampling...
		WiFiAPList l[] = new WiFiAPList[N];
		int downSamplingCounter = 0;
		l[downSamplingCounter++] = rawFPList[0];
		int prevIndex = 0;
		int n;
		for(int i = 1 ; i < N; ++i){

			int downsampleIndex = i;
                        try {
	  	       	  if((rawFPList[i].timeStamp - rawFPList[prevIndex].timeStamp) > (samplingIntervalOption[samplingIntervalIndex] * 1000)){
	  	       	  	long targetTime = rawFPList[prevIndex].timeStamp + samplingIntervalOption[samplingIntervalIndex] * 1000;
	  	       	  	if(Math.abs(rawFPList[i].timeStamp - targetTime) > Math.abs(rawFPList[i-1].timeStamp - targetTime)){
	  	       	  		if( (i-1) != prevIndex){
	  	       	  			downsampleIndex = (i-1);
	  	       	  		}
	  	       	  	}

	  	       	  	l[downSamplingCounter++] = rawFPList[downsampleIndex];		
	  	       	  	prevIndex = downsampleIndex;
	  	       	  }
                        }
                        catch (Exception e) {
                           System.err.println("Continuing ... some weird error \n");
                           continue;
                        }

		}
		n = downSamplingCounter;
		// done
	
		int firstRawDataInCurrentWindow = 0;
		for(int i = 1; i < n; ++i){
			if( l[i].timeStamp - l[firstRawDataInCurrentWindow].timeStamp > TIMEWINDOW_INTERVAL){

				WiFiAPList currentAPList[] = new WiFiAPList[i - firstRawDataInCurrentWindow];
				int counter = 0;
				for(int j = firstRawDataInCurrentWindow; j < i; ++j){
					//System.out.println(l[j]);
					currentAPList[counter++] = l[j];	
				}
				int totalNumInWindow  = counter;

				/* extract features */
				/* Feature 1: average common number of cell towers ratio */
				/* Feature 2: average rssi difference */
				/* Feature 3: average Tanimoto Distance */
				double aveCommonAPNumberRatio = 0.0;
				double aveRssiDifference = 0.0;
				double aveTanimotoDistance = 0.0;
				if(totalNumInWindow > 1){
					for(int j = 1; j < totalNumInWindow; ++j){
						
						int unionAPNum = unionAPNum(currentAPList[j-1], currentAPList[j]);
						if(unionAPNum == 0){
							aveCommonAPNumberRatio += 0;

						}else{	
							aveCommonAPNumberRatio += sameAPNum(currentAPList[j-1], currentAPList[j])/(double)unionAPNum(currentAPList[j-1], currentAPList[j]);	
						}
						aveTanimotoDistance += TanimotoDistance(currentAPList[j-1], currentAPList[j]);
						
						if(unionAPNum == 0){
							aveRssiDifference += 10;
						}else{
						aveRssiDifference += calDistance(currentAPList[j-1], currentAPList[j])/(double) unionAPNum(currentAPList[j-1], currentAPList[j]);
						}
						}
					aveCommonAPNumberRatio /= (totalNumInWindow - 1) * 1.0;
					aveRssiDifference /= (totalNumInWindow - 1) * 1.0;
					aveTanimotoDistance /= (totalNumInWindow - 1) * 1.0;

				}
				/* Feature 4: Tanimoto difference between the 1st and last fingerprint in the time window */
				double firstLastDifference = TanimotoDistance(currentAPList[0] , currentAPList[totalNumInWindow-1]);

				/* */
				try{

					Random r = new Random();
					String outFeature = aveCommonAPNumberRatio +","+ aveRssiDifference + ","+ aveTanimotoDistance + 
					      ","+firstLastDifference +","+ groundTruth+"\n";
					//System.out.println(outFeature);
						bufWriterOutArr[samplingIntervalIndex].write(outFeature);
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

	// windowing... //
	public static WiFiAPList generateWindowAPList(WiFiAPList[] a){
		int WINDOWSIZE = 3;
		int TRUSTOCCURENCE = 2;


		Map<String, Integer> hashTable = new HashMap<String, Integer>();
		double time = 0;
		for(WiFiAPList oneFingerPrint: a){
			//System.out.println(oneFingerPrint);
			time += oneFingerPrint.timeStamp;

			for(int i = 0; i < oneFingerPrint.APList.size(); ++i){
				String currentMac = oneFingerPrint.APList.get(i).mac;
				Integer count = hashTable.get(currentMac);
				hashTable.put(currentMac, (count == null)? 1:count+1);
			}
		}


		int time_int = (int) Math.round(time/WINDOWSIZE);
		List<AP> l = new ArrayList<AP>();
		Set<String> stringKeySet = hashTable.keySet();
		Iterator<String> it = stringKeySet.iterator();

		while( it.hasNext() ){ // for each key
			String key = it.next();
			int occurenceNum = hashTable.get(key);

			if(occurenceNum >= TRUSTOCCURENCE){
				double aveRssi = 0;
				for(WiFiAPList oneFingerPrint : a){
					for(int i = 0; i < oneFingerPrint.APList.size(); ++i){

						if(oneFingerPrint.APList.get(i).mac.equals(key)){
							aveRssi += oneFingerPrint.APList.get(i).rssi; 		
						}
					}
				}
				aveRssi /= occurenceNum;
				l.add(new AP(key,aveRssi));
			}
		}

		WiFiAPList result = new WiFiAPList(time_int, l);
		return result;
	}

	public static void initAPList(WiFiAPList[] l){
		for(int i = 0; i < l.length; ++i){
			l[i] = null;
		}
	}

	public static double TanimotoDistance(WiFiAPList a, WiFiAPList b){
		
		double aLength = 0.0;
		double bLength = 0.0;
		double dotValue = 0.0;
		for(int i = 0; i < a.APList.size(); ++i){
			aLength += a.APList.get(i).rssi * a.APList.get(i).rssi; 


			for(int j = 0; j < b.APList.size(); ++j){
				
				bLength += b.APList.get(j).rssi * b.APList.get(j).rssi;

				if(a.APList.get(i).mac.equals(b.APList.get(j).mac)){
					dotValue += a.APList.get(i).rssi * b.APList.get(j).rssi;	
				}
			
			}
		}
		
		return dotValue == 0? 0 : (dotValue/(aLength + bLength - dotValue));
	}
	public static double calDistance(WiFiAPList a, WiFiAPList b){


		boolean aFound[] = new boolean[a.APList.size()];
		boolean bFound[] = new boolean[b.APList.size()];
		int counter = 0;
		double distance = 0;
		for(int i = 0; i < a.APList.size(); ++i){

			for(int j = 0; j < b.APList.size(); ++j){

				if(a.APList.get(i).mac.equals(b.APList.get(j).mac)){

					aFound[i] = true;
					bFound[j] = true;
					distance+= Math.pow((a.APList.get(i).rssi - b.APList.get(j).rssi),2);
					++counter;
					break;
				}
			}
		}
		for(int i = 0; i < a.APList.size(); ++i){
			if(aFound[i] == false){
				distance+= Math.pow(a.APList.get(i).rssi + 99,2);
			}
		}
		for(int j = 0; j < b.APList.size(); ++j){
			if(bFound[j] == false){
				distance+= Math.pow(b.APList.get(j).rssi + 99,2);
			}
		}

		return Math.sqrt(distance);
	}

	public static int sameAPNum(WiFiAPList a, WiFiAPList b){

		int counter = 0;
		for(int i = 0; i < a.APList.size(); ++i){

			for(int j = 0; j < b.APList.size(); ++j){

				if(a.APList.get(i).mac.equals( b.APList.get(j).mac)){
					++counter;
					break;
				}
			}

		}

		return counter;
	}

	public static int unionAPNum(WiFiAPList a, WiFiAPList b){
		int intersect = sameAPNum(a, b);
		return (a.APList.size()+b.APList.size()-intersect);
	}
}


class WiFiAPList{

	List<AP> APList;
	long timeStamp;

	public WiFiAPList(){
		APList = new ArrayList<AP>();
	}
	public WiFiAPList(long time, String s){
		this.APList = new ArrayList<AP>();
		this.timeStamp = time;

		//356441045935745,1349407899513.1902,Wifi,3|MIT|00:21:d8:49:98:62|-85|5|1|MIT SECURE|00:26:cb:f4:13:03|-88|2437|TOPOFTHEHUB2|00:1a:70:fd:f0:49|-88|2442|MIT GUEST|00:21:d8:49:98:61|-87|2462|MIT|00:21:d8:49:98:62|-85|2462|MIT SECURE|00:26:cb:f4:14:03|-84|24123
		String segLine[] = s.split("\\|");
		String header[] = segLine[0].split(",");

		int apNum = Integer.parseInt(segLine[4]);
		for(int i = 0; i < apNum; ++i){
			String macAdd = segLine[6 + 4*i + 1];
			AP ap = new AP( macAdd, Double.parseDouble(segLine[6 + 4*i + 2]));

			int j = 0;
			for(j = 0; j < APList.size(); ++j){
				if(APList.get(j).mac.equals(macAdd)){
					break;
				}	
			}
			if( j == APList.size()){
				this.APList.add(ap);
			}
		}


	}
	public String toString(){
		//DecimalFormat df = new DecimalFormat("#############");
		String result = timeStamp + "," + APList.size() + ",";
		if(APList.size() > 0){
			for(int i = 0; i < APList.size(); ++i){
				result += APList.get(i).mac + "|" + APList.get(i).rssi + "|";
			}
		}
		return result;
	}
	public WiFiAPList(long time, List<AP> l){
		this.timeStamp = time;
		this.APList = l;	
	}
}
class AP{

	String mac;
	double rssi;

	public AP(String mac, double rssi){

		this.mac = mac;
		this.rssi = rssi;

	}

}
