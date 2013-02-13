class DecisionTree(object):

	fv = {}

	def __init__(self,fv):
		self.fv = fv

		self.classify()
	def classify(self):
		 p = self.N30f7f5400()
		 return p

	def N30f7f5400(self):

		p = 0
		if self.fv['var'] <= 0.014470164221:
			p = self.N670655dd1()
		elif self.fv['var'] > 0.014470164221:
			p = self.N50ef55022()
		return p

	def N670655dd1(self):

		p = 0
		if self.fv['speed'] <= 1.06335:
			p = 0
		elif self.fv['speed'] > 1.06335:
			p = 4
		return p

	def N50ef55022(self):

		p = 3
		if self.fv['speed'] <= 8.01561:
			p = self.N10b61fd13()
		elif self.fv['speed'] > 8.01561:
			p = 4
		return p

	def N10b61fd13(self):

		p = 3
		if self.fv['var'] <= 18.3361179313:
			p = self.N24e2dae94()
		elif self.fv['var'] > 18.3361179313:
			p = self.N27ce2dd47()
		return p

	def N24e2dae94(self):

		p = 1
		if self.fv['speed'] <= 1.6263:
			p = self.N299209ea5()
		elif self.fv['speed'] > 1.6263:
			p = self.N32c8f6f86()
		return p

	def N299209ea5(self):

		p = 3
		if self.fv['var'] <= 3.20099518737:
			p = 3
		elif self.fv['var'] > 3.20099518737:
			p = 1
		return p

	def N32c8f6f86(self):

		p = 4
		if self.fv['var'] <= 0.259066462337:
			p = 4
		elif self.fv['var'] > 0.259066462337:
			p = 3
		return p

	def N27ce2dd47(self):

		p = 1
		if self.fv['speed'] <= 1.8200275:
			p = self.N5122cdb68()
		elif self.fv['speed'] > 1.8200275:
			p = 2
		return p

	def N5122cdb68(self):

		p = 1
		if self.fv['3hz'] <= 211.66786392:
			p = 1
		elif self.fv['3hz'] > 211.66786392:
			p = 2
		return p
