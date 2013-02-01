class DecisionTree(object):

	fv = {}

	def __init__(self,fv):
		self.fv = fv

		self.classify()
	def classify(self):
		 p = self.Nb34bed00()
		 return p

	def Nb34bed00(self):

		p = 1
		if self.fv['speed'] <= 1.8200275:
			p = self.N33db4f6f1()
		elif self.fv['speed'] > 1.8200275:
			p = self.N670655dd6()
		return p

	def N33db4f6f1(self):

		p = 0
		if self.fv['var'] <= 0.178877824492:
			p = 0
		elif self.fv['var'] > 0.178877824492:
			p = self.N33c1b022()
		return p

	def N33c1b022(self):

		p = 1
		if self.fv['3hz'] <= 202.149585758:
			p = self.N5f1121f63()
		elif self.fv['3hz'] > 202.149585758:
			p = 2
		return p

	def N5f1121f63(self):

		p = 3
		if self.fv['var'] <= 3.75127489502:
			p = 3
		elif self.fv['var'] > 3.75127489502:
			p = self.N5dccce3c4()
		return p

	def N5dccce3c4(self):

		p = 1
		if self.fv['2hz'] <= 58.8164198134:
			p = self.N30f7f5405()
		elif self.fv['2hz'] > 58.8164198134:
			p = 1
		return p

	def N30f7f5405(self):

		p = 1
		if self.fv['3hz'] <= 40.2363981976:
			p = 1
		elif self.fv['3hz'] > 40.2363981976:
			p = 2
		return p

	def N670655dd6(self):

		p = 4
		if self.fv['var'] <= 19.0582619494:
			p = self.N50ef55027()
		elif self.fv['var'] > 19.0582619494:
			p = 2
		return p

	def N50ef55027(self):

		p = 3
		if self.fv['speed'] <= 8.514693:
			p = self.N10b61fd18()
		elif self.fv['speed'] > 8.514693:
			p = 4
		return p

	def N10b61fd18(self):

		p = 4
		if self.fv['var'] <= 0.172595528232:
			p = 4
		elif self.fv['var'] > 0.172595528232:
			p = 3
		return p
