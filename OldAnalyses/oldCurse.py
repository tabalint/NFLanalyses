import pandas as pd

olddata = pd.read_csv("2000rushing.csv", index_col="Player")
print(olddata.loc["Robert Smith","Att"])

diff = []
for x in range(2001,2015):
    filename = str(x) + "rushing.csv"
    data = pd.read_csv(filename, index_col="Player")
    for player in data.index:
        if player in olddata.index:
            diff.append(str(x) + "," + player + "," + str(data.loc[player,"Att"]) + "," + str(data.loc[player,"Yds"]).replace(",","") + "," + str(olddata.loc[player,"Att"]) + "," + str(olddata.loc[player,"Yds"]).replace(",",""))
    del olddata        
    olddata = data
    
f=open('oldCurse.csv','w')
for ele in diff:
    f.write(ele +'\n')
f.close()
diff = []