using System;
using System.Collections.Generic;
using System.Text;
using System.IO;

namespace GeoFencing
{
    class Program
    {
	// Guess this picks from system time ?
        static int Seed = new Random().Next();
        static Random Random = new Random(Seed);
        static string BaseDir = @"Data";
        static string ResultsFile = "results.csv";

	/* Main program */
        static void Main(string[] args)
        {
            if (File.Exists(ResultsFile))
            {
                File.Delete(ResultsFile); 				// Delete results.csv
            }
            
            for (int i = 0; i < 182; i++) 				// 182 users 
            {
                List<List<DataPoint>> data = ReadData(i); 		// each trajectory is a list, read all trajectories of a given user
                List<DataPoint> dataPoints = Stitch(data);		// stitch them together.

                List<Geofence> randomGeofences = GetRandomGeofences(dataPoints, 20); // Choose a set of random geofences for sim.
                for (int j = 1; j <= 20; j++)
                {
                    Console.WriteLine(i + " " + j); 			// progress indicator
                    List<Geofence> geofences = randomGeofences.GetRange(0, j); // pick first j geofences
                    
                    Results results = Simulate(dataPoints, geofences); // meat of the code, actually simulate
                    string line = string.Format("{0},{1},{2},{3},{4},{5},{6},{7},{8}", // csv format
                        dataPoints[0].UserId, j,			// makes sense
                        results.TotalTime, results.StayTime, results.MoveTime,
                        results.LengthGPS, results.LengthWifi, results.LengthGSM,
                        (results.LengthAccl * 5), results.Mismatch);

                    StreamWriter sw = new StreamWriter(ResultsFile, true);
                    sw.WriteLine(line);
                    sw.Close();
                }                
            }            
        }

	/* Actual Simulation */
        static Results Simulate(List<DataPoint> dataPoints, List<Geofence> geofences)
        {
            Results results = new Results();				// output of simulation

            HashSet<int> gtCurrentlyInside = new HashSet<int>();
            HashSet<int> currentlyInside = new HashSet<int>();

            bool shouldSampleGSM = true;
            bool shouldSampleWifi = false;
            bool shouldSampleGPS = false;
            int nextSamplingIndex = 0;
            int count = 0;


            int moveTime = 0;
            int stayTime = 0;

            for (int i = 0; i < dataPoints.Count; i++)
            {
                DataPoint dataPoint = dataPoints[i];

                if (dataPoint.MoveHint == 0)
                    stayTime++;
                else
                    moveTime++;

                int minGeofence = -1;
                double gsmDistance = GetNearestGeofenceDistance(dataPoint.GSMLocation, 2, geofences, ref minGeofence);
                double wifiDistance = GetNearestGeofenceDistance(dataPoint.WifiLocation, 0.2, geofences, ref minGeofence);
                double gpsDistance = GetNearestGeofenceDistance(dataPoint.Location, 0, geofences, ref minGeofence);
                int moveHint = dataPoint.MoveHint;
                
                // Get all the geofences I am currently inside
                HashSet<int> geofencesIndex = GetGeofencesSurrounding(dataPoint.Location, geofences);

		// If you are inside atleast one geofence
                if (gpsDistance < 0)
                {
                    // Iterate through all the geofences I am current inside
                    foreach (int gIndex in geofencesIndex)
                    {
                    	// If the ground truth does not the geofence 
                        if (!gtCurrentlyInside.Contains(gIndex))
                        {
                            // Add it to ground truth
                            gtCurrentlyInside.Add(gIndex);
                        }
                    }
                }

		// This snippet is to remove the geofence from ground truth if I am left any geofence
		// Iterate through the ground truth geofences
                foreach (int cIndex in gtCurrentlyInside.ToList())
                {
                    // Am I currently inside this geofence
                    if (!geofencesIndex.Contains(cIndex))
                    {
                    	// If not delete it
                        gtCurrentlyInside.Remove(cIndex);
                    }
                }

                if (nextSamplingIndex < i)
                {
                    throw new Exception();
                }

                results.LengthAccl++;
                if (i != 0 && moveHint == 0)
                {                    
                    nextSamplingIndex++;
                }

                if (i == nextSamplingIndex)
                {
                    if (shouldSampleGSM)
                    {
                        results.LengthGSM++;
                        if (gsmDistance <= 0)
                        {
                            count++;
                            shouldSampleWifi = true;
                        }
                        else
                        {
                            int offset = GetSamplingOffset(gsmDistance);
                            nextSamplingIndex = i + offset + 1;
                        }
                    }

                    if (shouldSampleWifi)
                    {
                        results.LengthWifi++;
                        if (wifiDistance <= 0)
                        {
                            shouldSampleGPS = true;
                        }
                        else
                        {
                            if (wifiDistance < 0.2)
                            {                                
                                shouldSampleGSM = false;
                                shouldSampleWifi = true;
                                shouldSampleGPS = false;
                            }
                            else
                            {
                                shouldSampleGSM = true;
                                shouldSampleWifi = false;
                                shouldSampleWifi = false;
                            }

                            int offset = GetSamplingOffset(wifiDistance);
                            nextSamplingIndex = i + offset + 1;
                        }
                    }

                    if (shouldSampleGPS)
                    {
                        results.LengthGPS++;
                        if (gpsDistance < 0)
                        {
                            foreach (int gIndex in geofencesIndex)
                            {
                                if (!currentlyInside.Contains(gIndex))
                                {
                                    currentlyInside.Add(gIndex);
                                }
                            }

                            nextSamplingIndex = i + 1;
                        }
                        else
                        {
                            if (gpsDistance < 0.2)
                            {                                
                                shouldSampleGSM = false;
                                shouldSampleWifi = true;
                                shouldSampleGPS = false;
                            }
                            else
                            {
                                shouldSampleGSM = true;
                                shouldSampleWifi = false;
                                shouldSampleGPS = false;
                            }

                            int offset = GetSamplingOffset(gpsDistance);
                            nextSamplingIndex = i + offset + 1;
                        }

                        foreach (int cIndex in currentlyInside.ToList())
                        {
                            if (!geofencesIndex.Contains(cIndex))
                            {
                                currentlyInside.Remove(cIndex);
                            }
                        }
                    }

                    if (currentlyInside.Count != 0)
                    {
                        shouldSampleGSM = false;
                        shouldSampleWifi = false;
                        shouldSampleGPS = true;
                    }
                }                

                if (!IsMatch(gtCurrentlyInside, currentlyInside))
                {
                    results.Mismatch++;
                }

                //Console.WriteLine(gsmDistance + " " + wifiDistance + " " + gpsDistance + " " + moveHint);
            }

            results.MoveTime = moveTime * 5;
            results.StayTime = stayTime * 5;
            results.TotalTime = dataPoints.Count * 5;

            return results;
        }

        static int GetSamplingOffset(double distance)
        {
            double speed = 200;
            double time = ((distance / speed) * (3600 / 5));
            time--;

            if (time > (3600 / 5))
            {
                time = (3600 / 5);
            }

            if (time < 0)
            {
                time = 0;
            }
             

            return (int)time;
        }

        static bool IsMatch(HashSet<int> lst1, HashSet<int> lst2)
        {
            foreach (int a in lst1)
            {
                if (!lst2.Contains(a)) return false;
            }

            foreach (int b in lst2)
            {
                if (!lst1.Contains(b)) return false;
            }

            return true;
        }

        static HashSet<int> GetGeofencesSurrounding(Location location, List<Geofence> geofences)
        {
            HashSet<int> lst = new HashSet<int>();

            for (int i = 0; i < geofences.Count; i++)
            {
                double distance = GetDistanceInKm(location, geofences[i].Location);
                distance -= geofences[i].Radius;
                if (distance < 0)
                {
                    lst.Add(i);
                }
            }

            return lst;
        }

	/* Pick the minimum distance GeoFence using the algorithm given below */
        static double GetNearestGeofenceDistance(Location location, double accuracy, List<Geofence> geofences, ref int minIndex)
        {
            double minDistance = double.MaxValue;
            minIndex = -1;
            for (int i = 0; i < geofences.Count; i++)
            {
                double distance = GetDistance(location, accuracy, geofences[i]);
                if (distance < minDistance)
                {
                    minDistance = distance;
                    minIndex = i;
                }
            }

            return minDistance;
        }

	/* Get distance from current location to centre of geofence */
        static double GetDistance(Location location, double accuracy, Geofence geofence)
        {
            double distance = GetDistanceInKm(location, geofence.Location);
            distance -= accuracy;
            distance -= geofence.Radius;

            return distance;
        }



        public static List<Geofence> GetRandomGeofences(List<DataPoint> dataPoints, int n)
        {
            List<Geofence> geofences = new List<Geofence>();

            int max = dataPoints.Count;

            for (int i = 0; i < n; i++)
            {
                int randomIndex = Random.Next(max);
                Location location = dataPoints[randomIndex].Location;

                Geofence geoFence = new Geofence()
                {
                    Location = new Location(location.Lat, location.Lng),
                    Radius = 0.2
                };

                geofences.Add(geoFence);
            }

            return geofences;
        }
	/* Interpolated Data */
        public static Location PerturbDataPointForGSM(Location location)
        {
            double deltaLat = Random.NextDouble() * 0.01;
            double deltaLong = Random.NextDouble() * 0.01;
            Location newLocation = new Location(location.Lat + deltaLat, location.Lng + deltaLong);
            return newLocation;
        }

        public static Location PerturbDataPointForWifi(Location location)
        {
            double deltaLat = Random.NextDouble() * 0.001;
            double deltaLong = Random.NextDouble() * 0.001;
            Location newLocation = new Location(location.Lat + deltaLat, location.Lng + deltaLong);
            return newLocation;
        }

        public static List<DataPoint> Stitch(List<List<DataPoint>> lstDataPoints)
        {
            List<DataPoint> newDataPoints = new List<DataPoint>();

            for (int i = 0; i < lstDataPoints.Count; i++)
            {
                List<DataPoint> dataPoints = lstDataPoints[i];
                newDataPoints.AddRange(dataPoints);

                if (i != lstDataPoints.Count - 1) /* Interpolate between two trajectories */
                {
                    List<DataPoint> fakeDataPoints = GenerateDataInBetweenPoints(dataPoints[dataPoints.Count - 1], lstDataPoints[i + 1][0]);
                    newDataPoints.AddRange(fakeDataPoints);
                }
            }

            return newDataPoints;
        }

        public static List<DataPoint> GenerateDataInBetweenPoints(DataPoint p1, DataPoint p2)
        {
            int randomStay1 = Random.Next(3600 / 5, 36000 / 5);
            int randomStay2 = Random.Next(3600 / 5, 36000 / 5);
            double distance = GetDistanceInKm(p1.Location, p2.Location);

            double speed = 6;
            if (distance < 2)
            {
                speed = new Random(Seed).Next(2, 10);
            }
            else if (distance > 10)
            {
                speed = Random.Next(30, 80);
            }
            else
            {
                speed = Random.Next(20, 50);
            }

            int time = (int)(distance / speed) * (3600 / 5);

            double latDelta = (p1.Location.Lat - p2.Location.Lat) / (double)time;
            double longDelta = (p1.Location.Lng - p2.Location.Lng) / (double)time;

            List<DataPoint> dataPoints = new List<DataPoint>();
            for (int i = 0; i < randomStay1; i++)
            {
                DataPoint dataPoint = new DataPoint()
                {
                    UserId = p1.UserId,
                    Location = new Location(p1.Location.Lat, p1.Location.Lng),
                    DataType = DataType.FakeStay,
                    MoveHint = 0
                };

                dataPoint.WifiLocation = PerturbDataPointForWifi(p1.Location);
                dataPoint.GSMLocation = PerturbDataPointForGSM(p1.Location);

                dataPoints.Add(dataPoint);
            }

	    /* Interpolation */
            for (int i = 1; i <= time; i += 10)
            {
                double lat = p1.Location.Lat + (i * latDelta);
                double lng = p1.Location.Lng + (i * longDelta);
                DataPoint dataPoint = new DataPoint()
                {
                    UserId = p1.UserId,
                    Location = new Location(lat, lng),
                    DataType = DataType.FakeMove,
                    MoveHint = 1
                };

                dataPoint.WifiLocation = PerturbDataPointForWifi(p1.Location);
                dataPoint.GSMLocation = PerturbDataPointForGSM(p1.Location);
                dataPoints.Add(dataPoint);
            }

            for (int i = 0; i < randomStay2; i++)
            {
                DataPoint dataPoint = new DataPoint()
                {
                    UserId = p2.UserId,
                    Location = new Location(p2.Location.Lat, p2.Location.Lng),
                    DataType = DataType.FakeStay,
                    MoveHint = (i == 0) ? 1 : 0
                };

                dataPoint.WifiLocation = PerturbDataPointForWifi(p2.Location);
                dataPoint.GSMLocation = PerturbDataPointForGSM(p2.Location);

                dataPoints.Add(dataPoint);
            }

            return dataPoints;
        }


	/* File IO routines */

        public static List<List<DataPoint>> ReadData(int userIndex)
        {
            List<List<DataPoint>> data = new List<List<DataPoint>>();

            string[] userDirs = Directory.GetDirectories(BaseDir);

            string user = userDirs[userIndex];
            string trajectoryDir = Path.Combine(userDirs[userIndex], "Trajectory");

            string[] trajectories = Directory.GetFiles(trajectoryDir);

            for (int j = 0; j < trajectories.Length; j++)
            {
                List<DataPoint> dataPoints = new List<DataPoint>();

                StreamReader sr = new StreamReader(trajectories[j]);
                for (int k = 0; k < 6; k++) sr.ReadLine();
                while (true)
                {
                    string line = sr.ReadLine();
                    if (line == null) break;

                    string[] splits = line.Split(new char[] { ',' });

                    DataPoint dataPoint = new DataPoint()
                    {
                        UserId = user,
                        Location = new Location(Convert.ToDouble(splits[0]), Convert.ToDouble(splits[1])),
                        DataType = DataType.Original,
                        MoveHint = 1
                    };

                    dataPoint.WifiLocation = PerturbDataPointForWifi(dataPoint.Location);
                    dataPoint.GSMLocation = PerturbDataPointForGSM(dataPoint.Location);

                    dataPoints.Add(dataPoint);
                }

                sr.Close();


                data.Add(dataPoints);
            }

            return data;
        }

        public static double GetDistanceInKm(Location l1, Location l2)
        {
            return GetDistanceInKm(l1.Lat, l1.Lng, l2.Lat, l2.Lng);
        }

        public static double GetDistanceInKm(double lat1, double lon1, double lat2, double lon2)
        {
            double R = 6371; // km
            double dLat = ConvertToRadians(lat2 - lat1);
            var dLon = ConvertToRadians(lon2 - lon1);
            lat1 = ConvertToRadians(lat1);
            lat2 = ConvertToRadians(lat2);

            var a = Math.Sin(dLat / 2) * Math.Sin(dLat / 2) +
                    Math.Sin(dLon / 2) * Math.Sin(dLon / 2) * Math.Cos(lat1) * Math.Cos(lat2);
            var c = 2 * Math.Atan2(Math.Sqrt(a), Math.Sqrt(1 - a));
            var d = R * c;

            return d;
        }

        private static double ConvertToRadians(double angle)
        {
            return (Math.PI / 180) * angle;
        }

        public static void SortByTime(List<DataPoint> dataPoints)
        {
            dataPoints.Sort(DataPointSorter);
        }

        private static int DataPointSorter(DataPoint d1, DataPoint d2)
        {
            if (d1.Time > d2.Time)
                return 1;

            if (d1.Time < d2.Time)
                return -1;

            return 0;
        }
    }
    

    public class DataPoint
    {
        public string UserId;
        public double Time;
        public Location Location;
        public Location WifiLocation;
        public Location GSMLocation;
        public double Accuracy;
        public DataType DataType;
        public int MoveHint;
    }

    public class Location
    {
        public double Lat;
        public double Lng;

        public Location(double lat, double lng)
        {
            this.Lat = lat;
            this.Lng = lng;
        }
    }

    public class Geofence
    {
        public Location Location;
        public double Radius;
    }

    public enum DataType
    {
        Original,
        FakeStay,
        FakeMove
    }

    public class Results
    {
        public int LengthGPS;
        public int LengthWifi;
        public int LengthGSM;
        public int LengthAccl;

        public int Mismatch;

        public int TotalTime;
        public int StayTime;
        public int MoveTime;        
    }
}
