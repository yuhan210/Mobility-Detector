
#! /usr/bin/python

from math import *
class Location(object):

	latitude = 0
	longitude = 0

	def __init__(self, lat, lon):
		self.latitude = lat
		self.longitude = lon
		self.canonicalize()

	def __str__(self):
		return 'lat:'+ str(self.latitude) +"\tlon:"+str(self.longitude)
	def canonicalize(self):
		self.latitude = (self.latitude + 180) % 360.0
		if (self.latitude < 0):
			self.latitude += 360
		else:
			self.latitude -= 180

		if (self.latitude > 90):
			self.latitude = 180 - self.latitude
			self.longitude += 180
		elif(self.latitude < -90):
			self.latitude = -180 - self.latitude
			self.longitude += 180

		self.longitude = ((self.longitude + 180) % 360.0)
		if self.longitude <= 0:
			self.longitude += 360
		else:
			self.longitude -= 180

	
	def compute_geo_distance(self, loc2):
	# the WGS84 ellipsoid	
		a = 6378137.0#semiMajorAxis
		f = 1.0/298.257223563
		b = (1.0 - f) * a

		phi1 = self.latitude * (pi / 180.0)
		lambda1 = self.longitude * (pi/ 180.0)
		phi2 = loc2.latitude * (pi/ 180.0)
		lambda2 = loc2.longitude * (pi/ 180.0)

		a2 = a * a
		b2 = b * b
		a2b2b2 = (a2 - b2) / b2

		omega = lambda2 - lambda1

		tanphi1 = tan(phi1)
		tanU1 = (1.0 - f) * tanphi1
		U1 = atan(tanU1)
		sinU1 = sin(U1)
		cosU1 = cos(U1)

		tanphi2 = tan(phi2)
		tanU2 = (1.0 - f) * tanphi2
		U2 = atan(tanU2)
		sinU2 = sin(U2)
		cosU2 = cos(U2)

		sinU1sinU2 = sinU1 * sinU2
		cosU1sinU2 = cosU1 * sinU2
		sinU1cosU2 = sinU1 * cosU2
		cosU1cosU2 = cosU1 * cosU2

		lambda_v = omega

		A = 0.0
		B = 0.0
		sigma = 0.0
		deltasigma = 0.0
		lambda0 = lambda_v
		converged = 0
		for i in range(20):
			lambda0 = lambda_v
			sinlambda = sin(lambda_v)
			coslambda = cos(lambda_v)

			sin2sigma = ( cosU2 * sinlambda * cosU2 * sinlambda ) + (cosU1sinU2 - sinU1cosU2 * coslambda) * (cosU1sinU2 - sinU1cosU2 * coslambda)
			sinsigma = sqrt(sin2sigma)

			cossigma = sinU1sinU2 + (cosU1cosU2 * coslambda)

			sigma = atan2(sinsigma, cossigma)
			
			if (sin2sigma == 0):
				sinalpha = 0.0
			else:
				sinalpha = cosU1cosU2 * sinlambda / sinsigma

			alpha = asin(sinalpha)
			cosalpha = cos(alpha)
			cos2alpha = cosalpha * cosalpha

			if (cos2alpha == 0):
				cos2sigmam = 0
			else:
				cos2sigmam = cossigma -2 * sinU1sinU2/cos2alpha
			
			u2 = cos2alpha * a2b2b2

			cos2sigmam2 = cos2sigmam * cos2sigmam

			A = 1.0 + u2 / 16384 * (4096 + u2 * ( -768 + u2 * (320 - 175 * u2)))

			B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74-47 * u2)))

			deltasigma = B * sinsigma * (cos2sigmam + B /4 * (cossigma * ( -1 +2 * cos2sigmam2) -B /6 * cos2sigmam * (-3 +4 * sin2sigma) * (-3 +4 *cos2sigmam2)))
			C = f/ 16 * cos2alpha * (4 + f * (4-3*cos2alpha))

			lambda_v = omega + (1- C) *f * sinalpha * (sigma + C *sinsigma * (cos2sigmam + C * cossigma * (-1+2* cos2sigmam2)))


			if lambda_v == 0: 
				change = 0.1
			else:
				change = abs((lambda_v-lambda0)/lambda_v)

			if (i > 1) and change < 0.000001:
				converged = 1
				break
			s = b * A * (sigma - deltasigma)
			#print "distance", s 

			return s
