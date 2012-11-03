Data Collection App: The Android application for data collection

groundTruth: 
0 - static
1 - walking
2 - running
3 - biking
4 - driving

---


GPS:

phoneID, Timestamp, GPS, GPSStatusCode|time from the satellite|lat|lon|altitude|accuracy|speed|bearing(heading)|groundTruth

example:
354957034256753,1343956473110.2941,GPS,2|1343956473000|37.3739755153656|-121.99373245239258|-31.0|6.0|0.0|0.0|4  					

---


WiFi:

phoneID, Timestamp, WiFi, WiFiState| current connected WiFi SSID| current connected WiFi BSSID | connected WiFi RSSI | number of neighboring wifi APs | groundTruth | SSID | BSSID | RSSI (level) | frequency| ....

example:
356441045935745,1349407899513.1902,Wifi,3|MIT|00:21:d8:49:98:62|-85|5|1|MIT SECURE|00:26:cb:f4:13:03|-88|2437|TOPOFTHEHUB2|00:1a:70:fd:f0:49|-88|2442|MIT GUEST|00:21:d8:49:98:61|-87|2462|MIT|00:21:d8:49:98:62|-85|2462|MIT SECURE|00:26:cb:f4:14:03|-84|24123

---

Accel:

phoneID, Timestamp, Accel, x | y | z| gt

example:
354957034256753,1342574445197.6473,Accel,-0.7627395|4.944186|7.8861814|0

---

GSM:

** Note!
There are two formats in the collected data

- New version - data collected after May, 2012

phoneID, Timestamp, GSM,  serving Cell ID| serving Cell LAC | serving Cell RSSI | serving network type | data state| groundTruth | number of neighboring cell towers | Cell ID | LAC | Rssi

example:
354957034256753,1342539419312.56,GSM,35463|6037|6|2|0|4|4|35464|6037|9|35466|6037|8|1235|6037|7|35461|6037|5

- Old Version - all of Tiffany's data collected before May, 2012

phoneID, Timestamp, GSM, serving Cell ID| serving Cell LAC | serving Cell RSSI | serving network type | data state| groundTruth | number of neighboring cell tower | Cell ID | Rssi

example:
355066049626536,1332202806532.5310,GSM,22181|6011|23|2|0|0|4|20561|14|20352|13|21511|16|22187|12

** Note!

- 99 is an invalid RSSI. RSSI can range from 0 to 32.
- CellIds are integers between 1 to 65535 (2 bytes)
- In the trace, if a cellId is greater than 65535, then only the first 2 bytes (n & 65535) represents the cellId. The higher 2 bytes is LAC code
which you can ignore.
- 0 means we did not see any cell Id at that point.
- Every cell tower scan in Android does not reliably return all cell towers.
So do windowing (we used window of 5 which works well).



---

Network Location:
phoneID, TimeStamp, Geo Loc, NWLoc status code | time | lat | lon | altitude | accuracy | speed | bearing(heading) | groundTruth

example:
354957034256753,1343970781751.2646,Geo Loc,1|1343970781736|37.3840827|-121.9934066|0.0|909.0|0.0|0.0|4


---

Mobility Detector: Codes for compute the activity recgnition accuracy for different sensors