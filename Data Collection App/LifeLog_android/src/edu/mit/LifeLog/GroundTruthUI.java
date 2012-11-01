package edu.mit.LifeLog;

import android.content.Context;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemSelectedListener;
import android.widget.ArrayAdapter;
import android.widget.CompoundButton;
import android.widget.Spinner;


public class GroundTruthUI {

	
	private Spinner GTSpinner;
	private static final String [] groundTruthChoices = {"Still", "Walking", "Running", "Biking","Driving"};
	
	public GroundTruthUI( Context context, ViewGroup container,
			LifeLogClient client){
		
		this.GTSpinner = new Spinner(context);
		
		GTUIListener gtListener = new GTUIListener();
		ArrayAdapter<String> groundTruthAdapter = new ArrayAdapter<String>(context, android.R.layout.simple_spinner_item,
				groundTruthChoices);
		GTSpinner.setOnItemSelectedListener(gtListener);
		GTSpinner.setSelection(0);
		GTSpinner.setAdapter(groundTruthAdapter);
		container.addView(GTSpinner);
		
	
	}
	class GTUIListener implements OnItemSelectedListener
	{

		public void handleGTChange(){
			String groundTruthChoice = (String)GTSpinner.getSelectedItem();
			   System.out.println("ground truth  = " + groundTruthChoice);
			   int gtNum = -1;
				if (groundTruthChoice.equals(groundTruthChoices[0]))
					gtNum = 0;					
				else if (groundTruthChoice.equals(groundTruthChoices[1]))
					gtNum = 1;		
				else if (groundTruthChoice.equals(groundTruthChoices[2]))
					gtNum = 2;
				else if (groundTruthChoice.equals(groundTruthChoices[3]))
					gtNum = 3;	
				else if (groundTruthChoice.equals(groundTruthChoices[4]))
					gtNum = 4;	
				else
					throw new RuntimeException("unknown ground truth spinner choice: " + groundTruthChoice); 
		
		
				Accl.setGroundTruth(gtNum);
				WiFi.setGroundTruth(gtNum);
				GSM.setGroundTruth(gtNum);
				GYRO.setGroundTruth(gtNum);
				Ort.setGroundTruth(gtNum);
				GPS.setGroundTruth(gtNum);
				Compass.setGroundTruth(gtNum);
				NWLoc.setGroundTruth(gtNum);
				Bluetooth.setGroundTruth(gtNum);
		}
		@Override
		public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
			//Toast.makeText(context, "You are "+parent.getSelectedItem().toString(), Toast.LENGTH_SHORT).show();
			
			System.out.println("Ground Truth spinner selected: " + parent);	
			handleGTChange();	
		}

		@Override
		public void onNothingSelected(AdapterView<?> arg0) {
		
			
		}

		
	}
}
