import pandas
import csv

class Experiment:
	
	def __init__(self, name, ID, i, backlog, sampleSize, intensity, duration, startSeason, seasons, farms):
		self.seasons = seasons
		self.farms = farms
		self.name = name
		self.ID = ID
		self.backlog = backlog
		self.sampleSize = sampleSize
		self.intensity = intensity
		self.duration = duration
		self.startSeason = startSeason
		self.fracDiv = i

	def prepData(self):
		with open(str(self.name) + '.csv', 'w') as csvfile:
			writer = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
			writer.writerow(['Experiment', 'Intensity', 'Duration', "Start of Shock", 'Season', 'Res', "FracDiv", 'Backlog', "sampleSize", "PriceT", "PriceS", 'Farm', 'Strategy', 'Monocrop', 'Funds', 'Acreage_T', 'Acreage_S', 'Labor', 'SeasonPD', "endPD", "Bankrupt"])
			for s in range(len(self.seasons)):
				season = self.seasons[s]
				priceT = self.seasons[s].marketPrice["tomato"]
				priceS = self.seasons[s].marketPrice["strawberry"]
				for farm in self.farms:
					num = farm.ID
					if farm.fundsList[s] <= 0 or farm.fundsList[s] == float("inf"):
						bankrupt = True
					else:
						bankrupt = False
					money = farm.fundsList[s]
					strategy = farm.strategyList[s]
					monocrop = farm.monocrop
					endPD = farm.probDiversify
					if (len(farm.probDiversifyList)-1) > s:
						seasonPD = farm.probDiversifyList[s]
					else:
						seasonPD = "NA"
					percentS = farm.percentSHarvested[s]
					percentT = farm.percentTHarvested[s]
					res = season.resilience
					labor = season.labor
					backlog = self.backlog
					sampleSize = self.sampleSize

					# Do this if you want to supply lists of options
					# intensity = ""
					# duration = ""
					# startSeason = ""
					# for i in range(len(self.intensity)):
					# 	intensity = intensity + str(self.intensity[i]) + "_"
					# 	duration = duration + str(self.duration[i]) + "_"
					# 	startSeason = startSeason + str(self.startSeason[i]) + "_"

					writer.writerow([self.ID, self.intensity, self.duration, self.startSeason, s, res, self.fracDiv, backlog, sampleSize, float(priceT), float(priceS), num, strategy, monocrop, money, percentT, percentS, labor, seasonPD, endPD, bankrupt])

		path = str(self.name)
		