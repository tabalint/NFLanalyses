import pandas as pd

noties = 0
tiesarray = []
for n in range(1966, 2016):
    print n
    filen = "boxscore" + str(n) + ".csv"
    databank = pd.read_csv(filen)
    ties = databank.loc[databank.loc[:,'W/L'] == "T",:]
    noties += len(ties)/2
    ties = databank.loc[databank.loc[:,'W/L'] == "T/OT",:]
    noties += len(ties)/2
    print noties
    tiesarray.append([n, noties, len(databank)/2])
    
print tiesarray