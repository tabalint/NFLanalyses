import nflgame as N
import pandas as pd

yearno=2009
data = pd.DataFrame(0, index=[2009,2010,2011,2012,2013,2014,2015], columns=["Touchdown", "Field Goal", "Interception", "Fumble", "Missed FG", "Blocked FG", "Safety", "Punt", "Blocked Punt", "Downs",  "End of Half", "End of Game", "Other"])
result=[]
while yearno<2016:
    weekno = 1
    while weekno<18:
        print "Week %d, %d" %(weekno,yearno)
        games = N.games(year=yearno, week=weekno, started=True)
        for g in games:
            no = 0
            for d in g.drives:
                no += 1
                result.append(d.field_start)
                if d.field_start != -1000:
                    if d.result == "Fumble, Safety":
                        data.loc[yearno,"Fumble"]+=1
                    elif d.result == "Blocked Punt, Downs":
                        data.loc[yearno,"Blocked Punt"]+=1
                    elif d.result == "Blocked FG, Downs":
                        data.loc[yearno,"Blocked FG"]+=1
                    elif d.result == "UNKNOWN" or d.result == "":
                        print g, d
                        data.loc[yearno,"Other"]+=1
                    else:
                        data.loc[yearno,d.result]+=1
            #print no
        weekno+=1
    yearno += 1

data.to_csv("DrivesByYear.csv")

#outfile = open('driveoutcomes.txt', 'w')
#for n in range(len(result)):
#    print(n)
#    outfile.write(str(result[n]))
#    outfile.write('\n')