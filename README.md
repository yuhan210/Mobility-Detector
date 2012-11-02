Data Collection App: The Android application for data collection

groundTruth: 
0 - static
1 - walking
2 - running
3 - biking
4 - driving

Data format: 

GPS:
phoneID, Timestamp, GPS, GPSStatusCode|time from the satellite|lat|lon|altitude|accuracy|speed|bearing(heading)|groundTruth

example:
354957034256753,1343956473110.2941,GPS,2|1343956473000|37.3739755153656|-121.99373245239258|-31.0|6.0|0.0|0.0|4  					


WiFi:
phoneID, Timestamp, WiFi, WiFiState| current connected WiFi SSID| current connected WiFi BSSID | connected WiFi RSSI | number of neighboring wifi APs | groundTruth | SSID | BSSID | RSSI (level) | frequency| ....

example:
356441045935745,1349407899513.1902,Wifi,3|MIT|00:21:d8:49:98:62|-85|5|1|MIT SECURE|00:26:cb:f4:13:03|-88|2437|TOPOFTHEHUB2|00:1a:70:fd:f0:49|-88|2442|MIT GUEST|00:21:d8:49:98:61|-87|2462|MIT|00:21:d8:49:98:62|-85|2462|MIT SECURE|00:26:cb:f4:14:03|-84|24123


Accel:
phoneID, Timestamp, Accel, x | y | z| gt

example:
354957034256753,1342574445197.6473,Accel,-0.7627395|4.944186|7.8861814|0

GSM:
phoneID, Timestamp, GSM,  connected Cell ID| connected Cell LAC | connected Cell RSSI | connected network type | connected data state| groundTruth | number of neighboring cell towers | Cell ID | LAC | Rssi

example:
354957034256753,1342539419312.56,GSM,35463|6037|6|2|0|4|4|35464|6037|9|35466|6037|8|1235|6037|7|35461|6037|5

Network Location:
phoneID, TimeStamp, Geo Loc, NWLoc status code | time | lat | lon | altitude | accuracy | speed | bearing(heading) | groundTruth

example:
354957034256753,1343970781751.2646,Geo Loc,1|1343970781736|37.3840827|-121.9934066|0.0|909.0|0.0|0.0|4


---

Mobility Detector: Codes for compute the activity recgnition accuracy for different sensors