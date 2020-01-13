library('ggplot2')
library('dplyr')
library('plotly')

loadData = function(name){
  path <- paste0("yourpathhere")
  df <- read.csv(path, header = FALSE, " ", skip = 1)
  names(df) = c('Experiment', 'Intensity', 'Duration', "Start of Shock", 'Season', 'Res', 'FracDiv', 'Backlog', "sampleSize", "PriceT", "PriceS", 'Farm', 'Strategy', 'Monocrop', 'Funds', 'Acreage_T', 'Acreage_S', 'Labor','SeasonPD','endPD', "Bankrupt") # for T50, take out seasonPD
  return(data.frame(df))
}

name = "newPrice_"
alldf = loadData("newPrice_2_0_0.csv")
booldf = data.frame("numD" = NA, "meanFunds" = NA,"Intensity" = NA, "Duration" = NA, "howmuch" = NA, "After" = NA, "betterthan" = NA)
specificFunds = data.frame("numD" = NA, "Intensity" = NA, "Duration" = NA, "Funds" = NA, "Type" = NA)
for (r in seq(2, 28, 2)){
  for (i in seq(1,10)){
    for (d in seq(1, 10)){
      newdf = loadData(paste0(name, r, "_", i, "_", d, ".csv"))
      alldf = rbind(alldf, newdf)
      afterdf = newdf[newdf$Season == d,]
      meanFunds = mean(afterdf$Funds)
      after = unique(afterdf$Monocrop[afterdf$Funds==max(afterdf$Funds)])
      if(after == "D"){
        nextBest = unique(afterdf$Monocrop[afterdf$Funds==max(afterdf$Funds[afterdf$Monocrop != "D"])])
        howmuch = mean(afterdf$Funds[afterdf$Monocrop=="D"], na.rm=T) - mean(afterdf$Funds[afterdf$Monocrop==nextBest], na.rm=T)
        betterThan = "both strawberry and tomato farms"
      } else {
        howmuch = mean(afterdf$Funds[afterdf$Monocrop==after],na.rm=T) - mean(afterdf$Funds[afterdf$Monocrop=="D"],na.rm=T)
        if (unique(afterdf$Monocrop[afterdf$Funds==min(afterdf$Funds)]) != "D"){
          betterThan = unique(afterdf$Monocrop[afterdf$Funds==min(afterdf$Funds)])
          if (betterThan == "S"){
            betterThan = "strawberry farms"
          } else if (betterThan == "T"){
            betterThan = "tomato farms"
          }
        } else {
          betterThan = "neither strawberry nor tomato farms"
        }
      }
      for (type in c("S", "D", "T")){
        funds = mean(afterdf$Funds[afterdf$Monocrop==type])
        specificFunds = rbind(specificFunds, data.frame("numD" = r, "Intensity" = i, "Duration" = d, "Funds" = funds, "Type" = type))
      }
      
      booldf = rbind(booldf, data.frame("numD" = r, "Intensity" = i, "Duration" = d,"meanFunds" =meanFunds, "howmuch" = howmuch, "After" = after, "betterthan" = betterThan))
    }
  }
}

booldf = booldf[-1,]
dGood = booldf[booldf$Intensity<10 & booldf$Duration<10,]
dGood$AfterSpecific <- dGood$After
dGood$After[dGood$After != "D"] <- "M"

# Fig 2
ggplot(specificFunds[-1,], aes(x = Intensity/10, y = Funds, color = Type,linetype = Type, group = Type)) +
  geom_smooth(se=FALSE) + theme_bw() + theme(panel.border = element_blank(),text=element_text(size=12), panel.grid.major = element_blank(),
                                             panel.grid.minor = element_blank(), axis.line = element_line(colour = "black")) +
  guides(size=FALSE) + labs(x = "Fraction of Total Labor Available", y = "Farm Funds (USD)") + 
  scale_color_manual(name = "Type of Farm", limits = c("S","D", "T"),
                     labels = c("S" = "Strawberry farms","D" = "Diversified farms",
                                "T" = "Tomato farms"),
                     values=c("#5e3c99", "#e66101", "deepskyblue3")) +
  scale_linetype_manual(name = "Type of Farm", limits = c("S","D", "T"),
                        labels = c("S" = "Strawberry farms","D" = "Diversified farms",
                                   "T" = "Tomato farms"),
                        values=c("twodash", "solid", "dashed"))

# Fig 3
a <- dGood[dGood$Intensity < 5,]
b <- dGood[dGood$Intensity == 5 | dGood$Intensity==6,]
c <- dGood[dGood$Intensity > 6,]
a$segment = "M more likely"
b$segment = "who the heck knows"
c$segment = "D more likely"
abc = rbind(a,b,c)
ggplot(abc, aes(x=numD, y = (log(howmuch+1)), color = segment)) +
  geom_smooth()

abcTab = data.frame("perc" = NA, "segment" = NA, "numD" = NA)
for(i in seq(2,28,2)){
  for(seg in c("M more likely", "who the heck knows", "D more likely")){
    guess="D"
    perc = nrow(abc[abc$numD==i & abc$segment==seg & abc$After==guess,])/nrow(abc[abc$numD==i & abc$segment==seg,])*100 
    abcTab = rbind(abcTab, data.frame("perc" = perc, "numD" = i, "segment" = seg))
  }
}
abcTab = abcTab[-1,]
abcTab$segment[abcTab$segment=="M more likely"] <- "a"
abcTab$segment[abcTab$segment=="who the heck knows"] <- "b"
abcTab$segment[abcTab$segment=="D more likely"] <- "c"
zm = matrix(abcTab$perc, nrow = length(unique(abcTab$segment)), ncol = length(unique(abcTab$numD)))
p1 <- ggplot(abcTab, aes(y = numD, x = segment, color = perc, size = perc)) + geom_point() +
  scale_color_continuous(low = "#5e3c99", high = "#e66101")


a <- dGood[dGood$Intensity == 1,] # Neither more likely
b <- dGood[dGood$Intensity == 2] # S or T more likely
c <- dGood[dGood$Intensity >= 3,] # Both more likely
a$segment = "Neither more likely"
b$segment = "S more likely"
c$segment = "Both more likely"
abc = rbind(a,b,c)
ggplot(abc, aes(x=numD, y = (log(howmuch+1)), color = segment)) +
  geom_smooth()

abcTab = data.frame("perc" = NA, "segment" = NA,"guess"=NA, "numD" = NA)
for(i in seq(2,28,2)){
  for(seg in c("Neither more likely", "S more likely", "Both more likely")){
    guess="strawberry farms"
    perc = nrow(abc[abc$numD==i & abc$segment==seg & (abc$betterthan=="strawberry farms" | abc$betterthan=="both strawberry and tomato farms"),])/nrow(abc[abc$numD==i & abc$segment==seg,])*100 
    abcTab = rbind(abcTab, data.frame("perc" = perc, "guess" = guess, "numD" = i, "segment" = seg))
  }
}
abcTab = abcTab[-1,]
abcTab$segment[abcTab$segment=="Neither more likely"] <- "a"
abcTab$segment[abcTab$segment=="S more likely"] <- "b"
abcTab$segment[abcTab$segment== "Both more likely"] <- "c"
zm = matrix(abcTab$perc, nrow = length(unique(abcTab$segment)), ncol = length(unique(abcTab$numD)))

p3 <- ggplot(abcTab, aes(y = numD, x = segment, color = perc, size = perc)) + geom_point() +
  theme_bw() + theme(panel.border = element_blank(),text=element_text(size=12), panel.grid.major = element_blank(),
                     panel.grid.minor = element_blank(), axis.line = element_line(colour = "black")) +
  guides(size=FALSE) + labs(title = "(a)",color="% Simulations \nin which Diversified\n Farms More Profitable Than\n Strawberry Farms", x = "Fraction of Total Labor Available", y = "Number of Diversified Farms") +
  scale_x_discrete(labels=c("a" = "0.1", "b" = "0.2",
                            "c" = "> 0.2")) +
  scale_y_continuous(breaks = seq(2, 28, by = 2)) +
  scale_color_continuous(low = "#5e3c99", high = "#e66101")

p4 <- p1 + theme_bw() + theme(panel.border = element_blank(),text=element_text(size=12), panel.grid.major = element_blank(),
                              panel.grid.minor = element_blank(), axis.line = element_line(colour = "black")) +
  guides(size=FALSE) + labs(title = "(b)", color="% Simulations \nin which Diversified\n Farms More Profitable Than \n All Monocropped Farms", x = "Fraction of Total Labor Available", y = "Number of Diversified Farms") +
  scale_x_discrete(labels=c("a" = "< 0.5", "b" = "0.5 and 0.6",
                            "c" = "> 0.6")) +
  scale_y_continuous(breaks = seq(2, 28, by = 2))

multiplot(p3,p4, cols = 2)
