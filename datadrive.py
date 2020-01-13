import xlrd
import pandas as pd
import numpy as np

hDf = pd.read_excel("historical_data.xlsx") # Get yourself an excel file from http://edis.ifas.ufl.edu/fe1026

nFarms = 3

alpha = 0.5

aToms = 0.2095277*100000
aStroobs = 0.8605836*100000

Sreq = 95 # /acre
Treq = 29 # /acre

p1 = 100
p2 = 100

# Yields 
tYield = list(hDf.T_Yield)
sYield = list(hDf.S_Yield)

# Labor cost per acre
# (Picking cost)
tLaborCost = 2408 # FE 1026
sLaborCost = 7788 # FE 1013

# Other production costs (preharvest + overhead)
tProdCost = 10078 # VanSickle
sProdCost = 12305 # FE 1013

# Elasticity (constant)
sE = -0.66498
tE = -0.58

minTPrice = min(hDf.T_Price)
minSPrice = min(hDf.S_Price)
maxTPrice = max(hDf.T_Price)
maxSPrice = max(hDf.S_Price)
sdTPrice = np.std(hDf.T_Price)
sdSPrice = np.std(hDf.S_Price)

tPrice = hDf.T_Price[0]
sPrice = hDf.S_Price[0]

startingFunds = (262020000/28000)*200 # Assume they planted tomatoes (https://www.nass.usda.gov/Quick_Stats/Ag_Overview/stateOverview.php?state=FLORIDA)
labor = [95*200*nFarms]*200 # *200 just so you don't run out of indices



