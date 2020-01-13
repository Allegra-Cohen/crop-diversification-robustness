import numpy as np 
import datadrive as dd

class Season:
	def __init__(self, marketPrice, cropProductivity, productionCosts, lastYields, elasticity, pMinimum, pMaximum, labor):
		self.marketPrice = marketPrice
		self.pMinimum = pMinimum
		self.pMaximum = pMaximum
		self.cropProductivity = cropProductivity
		self.productionCosts = productionCosts
		self.lastYields = lastYields
		self.elasticity = elasticity
		self.yieldVar = 0	
		self.labor = labor
		self.resilience = 0

	def calcResilience(self, farms):
		res = 0
		for f in farms:
			if not f.bankrupt:
				res += 1
		self.resilience = res/float(len(farms))


	def updatePrice(self, farms):
		yCurrent = self.getCurrentYields(farms)
		self.calculatePriceChange(yCurrent, False)
		for f in farms:
			f.marketPrice.append(self.marketPrice)


	def getCurrentYields(self, farms):
		totalYields = dict((k, 0) for k in farms[0].cropNames)
		yields = []
		for f in farms:
			if not f.bankrupt:
				for crop in f.expectedYields:
					if crop == "tomato" and f.percentTHarvested[len(f.percentTHarvested)-1] != float("inf") and f.percentTHarvested[len(f.percentTHarvested)-1] != float("-inf"):
						eYield = f.expectedYields[crop]*f.percentTHarvested[len(f.percentTHarvested)-1]
					elif crop == "strawberry" and f.percentSHarvested[len(f.percentSHarvested)-1] != float("inf") and f.percentSHarvested[len(f.percentSHarvested)-1] != float("-inf"):
						eYield = f.expectedYields[crop]*f.percentSHarvested[len(f.percentSHarvested)-1]
					else:
						eYield = 0
					yields.append(eYield)
					totalYields[crop] = totalYields[crop] + eYield # Stacking up yields for each crop over all the farms
		self.yieldVar = np.var(yields)
		return totalYields


	def calculatePriceChange(self, yCurrent, peek):
	# Seasons only keep track of one market price (their own)
		pNew = dict((k,0) for k in self.marketPrice.keys())
		if yCurrent["tomato"] != 0:
			pNew["tomato"] = max(0, (dd.aToms*(yCurrent["tomato"]**self.elasticity["tomato"]))/((dd.nFarms)**self.elasticity["tomato"]))
		else:
			pNew["tomato"] = dd.maxTPrice

		if yCurrent["strawberry"] != 0:
			pNew["strawberry"] = max(0, (dd.aStroobs*(yCurrent["strawberry"]**self.elasticity["strawberry"]))/((dd.nFarms)**self.elasticity["strawberry"]))
		else:
			pNew["strawberry"] = dd.maxSPrice

		if peek:
			return pNew
		else:
			self.marketPrice = pNew
			self.lastYields = yCurrent

