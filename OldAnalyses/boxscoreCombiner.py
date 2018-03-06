import pandas as pd

databank = pd.read_csv("boxscore1966.csv")

for n in range(1967, 2016):
    print n
    filen = "boxscore" + str(n) + ".csv"
    databank = databank.append(pd.read_csv(filen))
    
databank.to_csv("boxscoreAll.csv")