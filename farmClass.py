import bruteForce as bf
import numpy as np
import datadrive as dd

np.random.seed = 1

class Farm:

	def __init__(self, IDnumber, plotNames, plotAreas, plotKeys, cropNames, cropProductivity, productionCosts, marketPrice, startingMoney, probDiversify, monocrop, riskThreshold):
		self.ID = IDnumber
		self.plotNames = plotNames
		self.plotAreas = plotAreas
		self.plotKeys = plotKeys
		self.cropNames = cropNames
		self.cropProductivity = cropProductivity
		self.productionCosts = productionCosts
		self.marketPrice = marketPrice
		self.expectedCost = 0   			 
		self.expectedProfit = 0 			 
		self.actualProfit = 0
		self.currentFunds = startingMoney    
		self.fundsList = [startingMoney]
		self.profitsList = []
		self.expectedYields = 0 			 
		self.bankrupt = False
		self.plotCrops = {}     			 
		self.strategyList = []
		self.probDiversifyList = [probDiversify]
		self.probDiversify = probDiversify   
		self.trashed = 0 					 
		self.percentTHarvested = []
		self.percentSHarvested = []
		self.riskThreshold = riskThreshold
		self.monocrop = monocrop

	def printFarm(self):
		print(" ========= Farm Number ", self.ID, " ======== ")
		print("Farm crops: acres -- ", self.plotCrops)
		print("Farm funds: $", self.currentFunds)
		print("Farm strategic history: ", self.strategyList)
		print("Farm diversification probability: ", self.probDiversify)

	def allocate(self, marketPrice, minmax, verbal, adjustPD, *strategy):
		if self.bankrupt:
			self.setExpectedYields(0)
			self.strategyList.append("NA")
		else:
			minProfit = self.expectedCost - self.currentFunds
			if adjustPD == False and self.monocrop == "T":
				allocationDict = bf2.brute(self.cropNames, self.plotNames, self.cropProductivity, self.productionCosts, marketPrice, self.plotKeys, minProfit, minmax, False, False, verbal)
			elif adjustPD == False and self.monocrop == "S":
				allocationDict = bf3.brute(self.cropNames, self.plotNames, self.cropProductivity, self.productionCosts, marketPrice, self.plotKeys, minProfit, minmax, False, False, verbal)
			else:
				allocationDict = bf.brute(self.cropNames, self.plotNames, self.cropProductivity, self.productionCosts, marketPrice, self.plotKeys, minProfit, minmax, False, False, verbal)
			if allocationDict == {} or allocationDict == None:
				print("Farm ", self.ID, " has gone bankrupt.")
				self.setBankrupt(True)
				self.strategyList.append("NA")
				return
			else:
				if np.random.binomial(1, self.probDiversify) == 1 and "D" in allocationDict.keys(): # Probability you choose diversification and that strategy exists based on constraints
					allocation = allocationDict["D"]
				elif "M" in allocationDict.keys(): # If you chose monocrop and that strategy exists
					allocation = allocationDict["M"]
				else:
					allocation = allocationDict["D"] # If you chose monocrop but monocrop isn't a strategy based on the constraints

				if "M" in strategy or "D" in strategy:
					allocation = allocationDict[strategy]

				crops, expectedCost, expectedProfit, expectedYields = allocation[0], allocation[4], allocation[2], allocation[5]
				self.plotCrops = {}
				self.setCrops(crops)
				self.setExpectedProfit(expectedProfit)
				self.setExpectedCost(expectedCost)
				self.setExpectedYields(expectedYields)
				self.updateStrategyList()
				return allocationDict

	def setExpectedProfit(self, expectedProfit):
		self.expectedProfit = expectedProfit

	def setExpectedCost(self, expectedCost):
		self.expectedCost = expectedCost

	def setExpectedYields(self, expectedYields):
		self.expectedYields = expectedYields

	def updateFunds(self):
		actualProfit = 0
		for crop in self.marketPrice[len(self.marketPrice) - 1].keys():
			if crop in self.plotCrops.keys():
				if crop == "strawberry":
					actualProfit += self.marketPrice[len(self.marketPrice) - 1][crop]*self.expectedYields[crop]*self.percentSHarvested[len(self.percentSHarvested)-1]
				else:
					actualProfit += self.marketPrice[len(self.marketPrice) - 1][crop]*self.expectedYields[crop]*self.percentTHarvested[len(self.percentTHarvested)-1]
		self.actualProfit = actualProfit
		self.profitsList.append(self.actualProfit)
		self.currentFunds = self.currentFunds + actualProfit - self.expectedCost
		self.fundsList.append(self.currentFunds)
		if self.currentFunds <= 0:
			self.setBankrupt(True)
			print("Farm ", self.ID, " has gone bankrupt.")


	def setBankrupt(self, bankrupt):
		self.bankrupt = bankrupt

	def setCrops(self, crops):
		for p in range(len(crops)):
			plot = crops[p]
			for c in range(len(plot)):
				if plot[c] == 1:
					if self.cropNames[c] in self.plotCrops.keys():
						self.plotCrops[self.cropNames[c]].append(self.plotAreas[p])
					else: 
	 					self.plotCrops[self.cropNames[c]] = [self.plotAreas[p]]


	 # We never actually use this, but it's here
	def updateProbDiversify(self, farms, season, backlog, sampleSize):
		selectedFarms = np.random.choice(farms, size = sampleSize, replace = False)
		
		profitsD = []
		profitsM = []

		coefficient = 1

		for f in selectedFarms:
			for n in range(1, backlog): 
				if len(f.strategyList) - n > 0:
					if f.strategyList[len(f.strategyList) - n] == "D":
						profitsD.append(f.actualProfit*np.exp(n)*coefficient)
					else:
						profitsM.append(f.actualProfit*np.exp(n)*coefficient)

		if len(profitsD) == 0: profitsD = [0]
		if len(profitsM) == 0: profitsM = [0]
		avgD = np.mean(profitsD)
		avgM = np.mean(profitsM)

		if avgD > avgM and np.var(profitsD) < self.riskThreshold and avgM != 0:
			self.probDiversify += dd.alpha*(avgD - avgM)/float(avgM)
			if self.probDiversify > 1:
				self.probDiversify = 1
		elif avgM > avgD and avgD != 0:
			self.probDiversify -= dd.alpha*(avgM - avgD)/float(avgD)
			if self.probDiversify < 0:
				self.probDiversify = 0
		self.probDiversify = max(0, self.probDiversify)
		self.probDiversify = min(1, self.probDiversify)
		self.probDiversifyList.append(self.probDiversify)

    # Look at what the monocroppers have done
	def peekMonocrop(self, farms, season, Treq, Sreq, sampleSize):
		monocroppers = [f for f in farms if f.strategyList[len(f.strategyList)-1] == "M"]
		if len(monocroppers) == 0:
			return
		if len(monocroppers) <= sampleSize:
			sampleSize = len(monocroppers) - 1
		selectedFarms = np.random.choice(monocroppers, size = sampleSize, replace = False)
		tTotal = 0
		sTotal = 0
		for f in selectedFarms:
			if "tomato" in f.plotCrops.keys():
				tTotal += (season.labor/[f.bankrupt for f in farms].count(False))/Treq
			else:
				sTotal += (season.labor/[f.bankrupt for f in farms].count(False))/Sreq

		return [tTotal, sTotal]

	# Guess what the prices will be if you harvest x% of i and y% of j based on the sums of monocroppers
	# This integrates with maximizeAcreage (tSum = peekMonocrop + x% of i, etc.)
	def guessPrice(self, season, tSum, sSum):
		newPrices = season.calculatePriceChange({"tomato": tSum, "strawberry": sSum}, True)
		return newPrices

	def updateStrategyList(self):
		if len(self.plotCrops.keys()) > 1:
			self.strategyList.append("D")   # Diversified
		else:
			self.strategyList.append("M")   # Monocropped

