#Given the path of the trance, the groundtruth, possible start time and ending time
#It saves your trace!
#It generates the corret trace folder in the same directory
 
import os

###
path = 'C:\Users\yuhan\Dropbox\CITA_DATA\Anirudh\\2012-09-25-17-56-53_biking_renameTheTrace'
groundTruth = 3 # 0- static, 1- walking, 2-running, 3-biking, 4-driving
startTime = 1348610318789 # in millisecond
endTime = 1348612348204 # in millisecond
###

correctedTracePath = path+'_updated'
#os.makedirs(correctedTracePath)

fListing = os.listdir(path)
for infile in fListing: ## for each file

    if infile.find('GPS') >= 0 or infile.find('Geo Loc')>=0: #infile is each trace directory name
        oldFile = open(path + '/' + infile)
        newFile = open(correctedTracePath + '/' + infile,'w')
        print infile
        for line in oldFile:  # for each line
            #phoneID, Timestamp, GPS, GPSStatusCode|time from the satellite|lat|lon|altitude|
            #accuracy|speed|bearing(heading)|groundTruth
            header = line.split(",")
            timeStamp = float(header[1])
            if timeStamp >= startTime and timeStamp <= endTime:
                info = line.split("|")
                info[8] = str(groundTruth)
                
                writeLine = '|'.join(info)
                newFile.write(writeLine + '\n')
            else:
                 newFile.write(line)
                 
        oldFile.close()
        newFile.close()
    elif infile.find('Accel') >= 0 or infile.find('orientation') >= 0: #infile is each trace directory name
        oldFile = open(path + '/' + infile)
        newFile = open(correctedTracePath + '/' + infile,'w')
        print infile             
        for line in oldFile:  # for each line
            #phoneID, Timestamp, Accel, x | y | z| gt
            header = line.split(",")
            timeStamp = float(header[1])
            if timeStamp >= startTime and timeStamp <= endTime:
                info = line.split("|")
                info[3] = str(groundTruth)
                writeLine = '|'.join(info)
                newFile.write(writeLine)
            else:
                 newFile.write(line)
                 
        oldFile.close()
        newFile.close()
    elif infile.find('GYRO') >= 0:
        oldFile = open(path + '/' + infile)
        newFile = open(correctedTracePath + '/' + infile,'w')
        print infile             
        for line in oldFile:  # for each line
            header = line.split(",")
            timeStamp = float(header[1])
            if timeStamp >= startTime and timeStamp <= endTime:
                info = line.split("|")
                info[3] = str(groundTruth)
                writeLine = '|'.join(info)
                newFile.write(writeLine)
            else:
                 newFile.write(line)
                 
        oldFile.close()
        newFile.close()
    elif infile.find('orientation') >= 0:
        oldFile = open(path + '/' + infile)
        newFile = open(correctedTracePath + '/' + infile,'w')
        print infile             
        for line in oldFile:  # for each line
            #phoneID, Timestamp, Accel, x | y | z| gt
            header = line.split(",")
            timeStamp = float(header[1])
            if timeStamp >= startTime and timeStamp <= endTime:
                info = line.split("|")
                info[3] = str(groundTruth)
                writeLine = '|'.join(info)
                newFile.write(writeLine)
            else:
                 newFile.write(line)
                 
        oldFile.close()
        newFile.close()
    elif infile.find('Wifi') >= 0: #infile is each trace directory name
        oldFile = open(path + '/' + infile)
        newFile = open(correctedTracePath + '/' + infile,'w')
        print infile
        for line in oldFile:  # for each line
#phoneID, Timestamp, WiFi, WiFiState| current connected WiFi SSID| current connected WiFi BSSID
#| connected WiFi RSSI | number of neighboring wifi APs | groundTruth | SSID | BSSID | RSSI (level) | frequency| ....
            header = line.split(",")
            timeStamp = float(header[1])
            if timeStamp >= startTime and timeStamp <= endTime:
                info = line.split("|")
                info[5] = str(groundTruth)
                writeLine = '|'.join(info)
                if int(info[4]) == 0:
                    newFile.write(writeLine + '\n')
                else:
                    newFile.write(writeLine)
            else:
                 newFile.write(line)
                 
        oldFile.close()
        newFile.close()
    elif infile.find('GSM') >= 0: #infile is each trace directory name
        print infile
        oldFile = open(path + '/' + infile)
        newFile = open(correctedTracePath + '/' + infile,'w')
        
        for line in oldFile:  # for each line
#phoneID, Timestamp, GSM, serving Cell ID| serving Cell LAC | serving Cell RSSI
#| serving network type | data state| groundTruth | number of neighboring cell towers | Cell ID | LAC | Rssi
            header = line.split(",")
            timeStamp = float(header[1])
            if timeStamp >= startTime and timeStamp <= endTime:
                info = line.split("|")
                info[5] = str(groundTruth)
                writeLine = '|'.join(info)
                newFile.write(writeLine)
            else:
                 newFile.write(line)
                 
        oldFile.close()
        newFile.close()
