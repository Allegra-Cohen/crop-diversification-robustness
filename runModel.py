import farmClass as fc
import experimentClass as exp
import seasonClass as sc
import datadrive as dd
import numpy as np
import operator 
import pandas as pd
from itertools import chain

def run(numFarms, plotNames, plotKeys, plotAreas, cropNames, numSeasons, initialMarketPrice, pMinimum, pMaximum, probDiversify, monocrop,
	cropProductivity, productionCosts, initialYields, elasticity, verbal, backlog, sampleSize, adjustPD, Sreq, Treq, intensity, duration,
	graph, shockTime):
	seasons = []
	marketPriceT = [initialMarketPrice["tomato"]]
	marketPriceS = [initialMarketPrice["strawberry"]]
	labor = readLabor(numSeasons, intensity, duration, shockTime)
	firstSeason = sc.Season(initialMarketPrice, cropProductivity[0:1], productionCosts[0:1], initialYields, elasticity, pMinimum, pMaximum, labor[0])
	farms = initializeFarms(numFarms, firstSeason, verbal, plotNames, plotKeys, plotAreas, cropNames, probDiversify, monocrop)
	laborReduce(farms, firstSeason, Sreq, Treq, 0)
	firstSeason.updatePrice(farms)
	updateFarms(farms, firstSeason, True, backlog, sampleSize, adjustPD)
	firstSeason.calcResilience(farms)
	lastSeason = firstSeason
	seasons.append(lastSeason)
	marketPriceT.append(lastSeason.marketPrice["tomato"])
	marketPriceS.append(lastSeason.marketPrice["strawberry"])

	for s in range(1,numSeasons): # Because you already did the first one
		if all([f.bankrupt for f in farms]):
			print(" Everyone's bankrupt, goodbye ")
			thisSeason = lastSeason
			seasons.append(lastSeason)
			remaining = numSeasons - s - 1
			marketPriceT = marketPriceT + [0]*remaining
			marketPriceS = marketPriceS + [0]*remaining
			allocateFarms(farms, thisSeason, verbal, True)
			break
		else:
			thisSeason = sc.Season(lastSeason.marketPrice, cropProductivity[0:s], productionCosts[0:s], lastSeason.lastYields, elasticity, pMinimum, pMaximum, labor[s]) # A season updates its yields before death
			allocateFarms(farms, thisSeason, verbal, False)
			laborReduce(farms, thisSeason, Sreq, Treq, s)
			thisSeason.updatePrice(farms)
			updateFarms(farms, thisSeason, False, backlog, sampleSize, adjustPD)
			thisSeason.calcResilience(farms)
			lastSeason = thisSeason
			seasons.append(lastSeason)
			marketPriceT.append(lastSeason.marketPrice["tomato"])
			marketPriceS.append(lastSeason.marketPrice["strawberry"])
	return (farms, thisSeason, marketPriceT, marketPriceS, seasons)



def readLabor(numSeasons, intensity, duration, shockTime):
	labor = dd.labor
	for i in range(0, duration):
		labor[shockTime+i] = labor[shockTime+i]*intensity
	return labor



def splitProportionally(current_acreageS, current_acreageT, farm_labor):
	sProportion = current_acreageS/float(current_acreageS + current_acreageT)
	return(farm_labor*sProportion, farm_labor*(1-sProportion))


def maximizeAcreage(acreageT, acreageS, season, Treq, Sreq, farm_labor, farm, n):

	adjustedTLabor = (dd.tLaborCost/(40000))*(season.cropProductivity[n-1]["tomato"]["Plot1"])
	adjustedSLabor = (dd.sLaborCost/(26400))*(season.cropProductivity[n-1]["strawberry"]["Plot1"])

	cropProf = {}
	for i in range(acreageT):				
		for j in range(acreageS):
			if i*Treq + j*Sreq <= farm_labor:
				tProfit = season.marketPrice["tomato"]*season.cropProductivity[n-1]["tomato"]["Plot1"]*i - adjustedTLabor*i 
				sProfit = season.marketPrice["strawberry"]*season.cropProductivity[n-1]["strawberry"]["Plot1"]*j - adjustedSLabor*j
				totalProfit = tProfit + sProfit
				cropProf[(i, j)] = totalProfit
	if bool(cropProf):
		bestAcreage = max(cropProf.items(), key=operator.itemgetter(1))[0]
		bestAcreage = {"tomato": [bestAcreage[0]], "strawberry": [bestAcreage[1]]}
		farm.expectedCost += adjustedSLabor*bestAcreage["strawberry"][0] + adjustedTLabor*bestAcreage["tomato"][0]
		if bestAcreage["tomato"][0] == 0:
			bestAcreage = {"strawberry": [bestAcreage["strawberry"][0]]} 
			farm.trashed += 1
		if bestAcreage["strawberry"][0] == 0:
			if "tomato" in bestAcreage.keys():
				bestAcreage = {"tomato": [bestAcreage["tomato"][0]]} 
			farm.trashed += 1
		
	else:
		bestAcreage = {"tomato": [0], "strawberry": [0]} 
		
	return bestAcreage




# Check that you have the required labor for the crops; if not, reduce the less lucrative crop acreage (assume funds are sunk costs)
# L/Treq = #people/acre
def laborReduce(farms, season, Sreq, Treq, n):
	farm_labor = season.labor/[f.bankrupt for f in farms].count(False) # Divide labor equally between farms still in business

	for farm in farms:					# For each farm, adjust the acreage harvested depending on the amount of available labor
		if not farm.bankrupt:
			if farm.strategyList[len(farm.strategyList)-1] == "D":
				oldAcreageT = farm.plotCrops["tomato"]
				oldAcreageS = farm.plotCrops["strawberry"]
				T = sum(farm.plotCrops["tomato"])*Treq
				S = sum(farm.plotCrops["strawberry"])*Sreq
				if (S + T > farm_labor): # If you have two different labor requirements
					farm.plotCrops = maximizeAcreage(farm.plotCrops["tomato"][0], farm.plotCrops["strawberry"][0], season, Treq, Sreq, farm_labor, farm, n)
				if "tomato" in farm.plotCrops.keys():
					farm.percentTHarvested.append(float(farm.plotCrops['tomato'][0])/oldAcreageT[0])
				else:
					farm.percentTHarvested.append(0)
				if "strawberry" in farm.plotCrops.keys():
					farm.percentSHarvested.append(float(farm.plotCrops['strawberry'][0])/oldAcreageS[0])
				else:
					farm.percentSHarvested.append(0)
			else:
				if "tomato" in farm.plotCrops.keys(): # If the farm didn't diversify this season and it planted tomatoes
					T = sum(farm.plotCrops["tomato"])*Treq
					farm.plotCrops["tomato"] = sum(farm.plotCrops["tomato"])
					oldAcreage = farm.plotCrops["tomato"]
					if T > farm_labor:
						newT = farm_labor/Treq # What you can harvest
						farm.plotCrops["tomato"] = newT
						farm.expectedCost += dd.tLaborCost*newT # Update cost with labor cost for the total acreage (you don't do this anywhere else)
					farm.percentTHarvested.append(float(farm.plotCrops['tomato'])/oldAcreage)
					farm.percentSHarvested.append(float('-inf'))
				else:
					S = sum(farm.plotCrops["strawberry"])*Sreq # Number of people needed
					farm.plotCrops["strawberry"] = sum(farm.plotCrops["strawberry"])
					oldAcreage = farm.plotCrops["strawberry"]
					if S > farm_labor:
						newS = farm_labor/Sreq
						farm.plotCrops["strawberry"] = newS
						farm.expectedCost += dd.sLaborCost*newS
					farm.percentSHarvested.append(float(farm.plotCrops['strawberry'])/oldAcreage)
					farm.percentTHarvested.append(float('-inf'))
		else:
			farm.percentTHarvested.append(float('inf'))
			farm.percentSHarvested.append(float('inf'))




def initializeFarms(numFarms, season, verbal, plotNames, plotKeys, plotAreas, cropNames, probDiversify, monocrop, *strategy):
	farms = []
	for n in range(numFarms):
		farm = fc.Farm(n, plotNames, plotAreas, plotKeys, cropNames, season.cropProductivity, season.productionCosts, [season.marketPrice], dd.startingFunds, probDiversify[n], monocrop[n], None)
		if "M" in monocrop or "D" in monocrop:
			farm.allocate([season.marketPrice], "max", verbal, monocrop[n])
		else:
			farm.allocate([season.marketPrice], "max", verbal, monocrop[n])
		farms.append(farm) 

	return farms




def allocateFarms(farms, thisSeason, verbal, end, *strategy):
	if end:
		for n in range(len(farms)):
			farms[n].strategyList.append("NA")
			farms[n].percentTHarvested.append(float("+inf"))
			farms[n].percentSHarvested.append(float("+inf"))
	else:
		for n in range(len(farms)):
			if "M" in strategy or "D" in strategy:
				farms[n].allocate([thisSeason.marketPrice], "max", verbal,monocrop[n], *strategy[n])
			else:
				farms[n].allocate([thisSeason.marketPrice], "max", verbal,monocrop[n])





def updateFarms(farms, season, first, backlog, sampleSize, adjustPD):
	for f in farms:
		if not f.bankrupt:
			f.updateFunds()
		else:
			f.fundsList.append(float("inf"))

	for f in farms:
		if not f.bankrupt:
			if adjustPD:
				f.updateProbDiversify(farms, season, backlog, sampleSize)

# =================================================================================================================================================================================================================================
# =================================================================================================================================================================================================================================
def optimWrapper(n, backlog, sampleSize, adjustPD, intensity, duration, shockTime, probDiversify, monocrop, graph):

	# Sreq = 1.12 # Workers/acre (Labor Shortages in the FL Strawberry Industry -- Guan, Revised)
	# Treq = 0.29 # Workers/acre (Calculated proportionally using hours/hectare requirements from Roka and Guan, 2018)

	plotNames = ["Plot1", "Plot2"]
	plotKeys = {"Plot1": dd.p1,
				 "Plot2": dd.p2}

	plotAreas = [dd.p1, dd.p2]
	cropNames = ["tomato", "strawberry"]
	elasticity = {"tomato": dd.tE, "strawberry":dd.sE}
	pMinimum = {"tomato": dd.minTPrice, "strawberry": dd.minSPrice}
	pMaximum = {"tomato": dd.maxTPrice, "strawberry": dd.maxSPrice}

	initialMarketPrice = {"tomato": dd.hDf.T_Price[len(dd.hDf.T_Price)-1], "strawberry": dd.hDf.S_Price[len(dd.hDf.S_Price)-1]}
	yieldList = []
	costList = []
	for i in range(n):
		yieldDict = {"tomato": {"Plot1": dd.tYield[len(dd.tYield)-n+i], "Plot2": dd.tYield[len(dd.tYield)-n+i]}, "strawberry": {"Plot1": dd.sYield[len(dd.tYield)-n+i], "Plot2": dd.sYield[len(dd.tYield)-n+i]}}
		
		yieldList.append(yieldDict)
		costDict = {"tomato": {"Plot1": (dd.tProdCost/40000)*dd.tYield[len(dd.tYield)-n+i], "Plot2": (dd.tProdCost/40000)*dd.tYield[len(dd.tYield)-n+i]}, "strawberry": {"Plot1": (dd.sProdCost/26400)*dd.sYield[len(dd.sYield)-n+i], "Plot2": (dd.sProdCost/26400)*dd.sYield[len(dd.sYield)-n+i]}} # Add labor costs in later
		costList.append(costDict)
	
	initialYields = {"tomato": sum(yieldList[len(yieldList) - n]["tomato"].values())*100*dd.nFarms, "strawberry":sum(yieldList[len(yieldList) - n]["strawberry"].values())*100*dd.nFarms}
	region = run(dd.nFarms, plotNames, plotKeys, plotAreas, cropNames,
		n, initialMarketPrice, pMinimum, pMaximum, probDiversify,monocrop, yieldList, costList, initialYields, elasticity,
		 False, backlog, sampleSize, adjustPD, dd.Sreq, dd.Treq, intensity, duration, graph, shockTime)
	farms, season, mpT, mpS, seasons = region[0], region[1], region[2], region[3], region[4]

	return([seasons, farms])


# =================================================================================================================================================================================================================================
# Scenarios
# =================================================================================================================================================================================================================================


n = 39
adjustPD = False
probDiversify = [0,0,1,1]
monocrop = ["S", "T", "D", "D"]
i = 2

# Breaks needs to be equal to or less than number of seasons
def runAll(breaks, name, shockTime):

	for b in range(breaks):
		for d in range(breaks):

			print("INTENSITY ", str(b), "DURATION ", str(d))

			intensity = float(b + 1)/10
			results = optimWrapper(n, backlog, sampleSize, adjustPD, intensity, d, shockTime, probDiversify, monocrop, False)
			ex = exp.Experiment(name + "_" + str(b+1) + "_" + str(d), str(b+1) + "_" + str(d), i, 0, 0, intensity, d, shockTime, results[0], results[1])
			ex.prepData()

# optimWrapper(seasons, historical availability, probability sampling size, % available labor, duration of shock, season to start the shock at, vector of initial diversification probabilities, graph or not)
# Experiment(filename, experiment number, intensity, duration, shock time, seasons, farms)
results = optimWrapper(4, 0, 0, adjustPD, 1, 1, 1, probDiversify, monocrop, False)
ex = exp.Experiment("funTest", "1", 2, 0,0, 1, 1, 1, results[0], results[1])
ex.prepData()


