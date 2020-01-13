import numpy as np
import itertools
import matplotlib.pyplot as plt

def getStats(cropNames, plotNames, cropProductivity, productionCosts, marketPrice, plotKeys, x):
	cov = []
	profitSum = 0
	varSum = 0
	totalCost = 0
	totalYields = dict((k, 0) for k in cropNames)
	for p in range(len(plotNames)):
		plot1 = plotNames[p]

		for c in range(len(cropNames)):
			crop1 = cropNames[c]
			ret = np.mean([a[crop1]*b[crop1][plot1] for a,b in zip(marketPrice, cropProductivity)])*plotKeys[plot1]*x[p][c]
			totalYields[crop1] = totalYields[crop1] + np.mean([a[crop1][plot1] for a in cropProductivity])*plotKeys[plot1]*x[p][c]
			cost = np.mean([a[crop1][plot1] for a in productionCosts])*plotKeys[plot1]*x[p][c]
			profitSum += ret - cost
			totalCost += cost

			for q in range(len(plotNames)):
				plot2 = plotNames[q]

				for k in range(len(cropNames)):

					crop2 = cropNames[k]
					d1 = [a[crop1]*b[crop1][plot1] for a,b in zip(marketPrice, cropProductivity)]
					d2 = [a[crop2]*b[crop2][plot2] for a,b in zip(marketPrice, cropProductivity)]
					if np.allclose(d1,d2):
						rho = (np.mean([i ** 2 for i in d1]) - (np.mean(d1))**2)
						val = rho*x[p][c]*x[q][k]*plotKeys[plot1]*plotKeys[plot2]
						cov.append(rho)
					else:
						rho = np.mean([a*b for a,b in zip(d1,d2)]) - np.mean(d1)*np.mean(d2)
						val = rho*x[p][c]*x[q][k]*plotKeys[plot1]*plotKeys[plot2]
						cov.append(rho)

					varSum = varSum + val
	
	return varSum, profitSum, cov, totalCost, totalYields


def validX(x, fallowing):
	good = True
	if (x[0][0] == x[0][1]) or (x[1][0] == x[1][1]):
		if fallowing == False:
			good = False
		elif fallowing and ((x[0][0] == x[0][1] and x[0][1] == 0) or (x[1][0] == x[1][1] and x[1][1] == 0)):
			good = True
	return good


def brute(cropNames, plotNames, cropProductivity, productionCosts, marketPrice, plotKeys, w, minmax, hist = False, fallowing = True, verbal = False):
	xlist = [0,1]
	alist = [p for p in itertools.product(xlist, repeat=2)]
	dOpts = []
	mOpts = []
	for a in alist: 
		for b in alist:

			a, b = list(a), list(b)
			x = [a, b]
			vals = getStats(cropNames, plotNames, cropProductivity, productionCosts, marketPrice, plotKeys, x)
			goodx = validX(x, fallowing)
			if (goodx): 
				if x[0][0] + x[1][0] == 2 or x[0][1] + x[1][1] == 2:
					mOpts.append([x, vals[0], vals[1], vals[2], vals[3], vals[4]])  # allocation, risk, profit, cov matrix, cost, yields
					
				else:
					dOpts.append([x, vals[0], vals[1], vals[2], vals[3], vals[4]]) 
				

	if verbal:
		if len(dOpts) == 0 and len(mOpts) == 0:
			print("\nNo options left after constraining :(\n")
			return

		else:
			print("\n")
			print(len(dOpts) + len(mOpts), " valid allocations")

	if minmax == "min":
		optsDict = {}
		if len(dOpts) != 0:
			dMinimum = min(dOpts, key=lambda x: x[1])
			optsDict["D"] = dMinimum
		if len(mOpts) != 0:
			mMinimum = min(mOpts, key=lambda x: x[1])
			optsDict["M"] = mMinimum
		return optsDict

	else:
		optsDict = {}
		if len(dOpts) != 0:
			dMaximum = max(dOpts, key=lambda x: x[2])
			optsDict["D"] = dMaximum
		if len(mOpts) != 0:
			mMaximum = max(mOpts, key=lambda x: x[2])
			optsDict["M"] = mMaximum
		return optsDict




