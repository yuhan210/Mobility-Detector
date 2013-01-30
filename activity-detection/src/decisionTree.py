class DecisionTree(object):

	fv = {}

	def __init__(self,fv):
		self.fv = fv

	def classify(self):
		 p = self.N33db4f6f0()
		 return p

	def N33db4f6f0(self):

		p = -1
		if self.fv['speed'] <= 1.8200275:
			p = self.N33c1b021()
		elif self.fv['speed'] > 1.8200275:
			p = self.N50ef55026()
		return p

	def N33c1b021(self):

		p = -1
		if self.fv['var'] <= 0.179130860299:
			p = 0
		elif self.fv['var'] > 0.179130860299:
			p = self.N5f1121f62()
		return p

	def N5f1121f62(self):

		p = -1
		if self.fv['3hz'] <= 201.840972895:
			p = self.N5dccce3c3()
		elif self.fv['3hz'] > 201.840972895:
			p = 2
		return p

	def N5dccce3c3(self):

		p = -1
		if self.fv['var'] <= 3.59194723988:
			p = 3
		elif self.fv['var'] > 3.59194723988:
			p = self.N30f7f5404()
		return p

	def N30f7f5404(self):

		p = -1
		if self.fv['2hz'] <= 58.6888205716:
			p = self.N670655dd5()
		elif self.fv['2hz'] > 58.6888205716:
			p = 1
		return p

	def N670655dd5(self):

		p = -1
		if self.fv['3hz'] <= 40.9097352392:
			p = 1
		elif self.fv['3hz'] > 40.9097352392:
			p = 2
		return p

	def N50ef55026(self):

		p = -1
		if self.fv['var'] <= 18.3397338976:
			p = self.N10b61fd17()
		elif self.fv['var'] > 18.3397338976:
			p = self.N299209ea9()
		return p

	def N10b61fd17(self):

		p = -1
		if self.fv['speed'] <= 9.0:
			p = self.N24e2dae98()
		elif self.fv['speed'] > 9.0:
			p = 4
		return p

	def N24e2dae98(self):

		p = -1
		if self.fv['var'] <= 0.172057869276:
			p = 4
		elif self.fv['var'] > 0.172057869276:
			p = 3
		return p

	def N299209ea9(self):

		p = -1
		if self.fv['speed'] <= 3.905125:
			p = 2
		elif self.fv['speed'] > 3.905125:
			p = 3
		return p
