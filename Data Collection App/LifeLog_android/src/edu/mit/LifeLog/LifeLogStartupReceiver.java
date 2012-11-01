package edu.mit.LifeLog;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

public class LifeLogStartupReceiver extends BroadcastReceiver
{
	@Override
	public void onReceive(Context context, Intent intent) 
	{
		/**if (intent.getAction().equals(Intent.ACTION_BOOT_COMPLETED)) 
		{
			
			System.out.println("starting LifeLog service");
			Intent i = new Intent();
			i.setAction("edu.mit.LifeLog.LifeLogService");
			context.startService(i);
		}**/
	}
}
