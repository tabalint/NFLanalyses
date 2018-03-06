import nflgame as N
import pandas as pd

yearno=2016
data = pd.DataFrame(0, index=[2009,2010,2011,2012,2013,2014,2015], columns=["Touchdown", "Field Goal", "Interception", "Fumble", "Missed FG", "Blocked FG", "Safety", "Punt", "Blocked Punt", "Downs",  "End of Half", "End of Game", "Other"])

result=[]
while yearno<2017:
    weekno = 1
    while weekno<18:
        print "Week %d, %d" %(weekno,yearno)
        games = N.games(year=yearno, week=weekno)
        for g in games:
            hometd, homepassint, homeatt, awaytd, awayint, awayatt=0,0,0,0,0,0
            for d in g.drives:
                for p in d.plays.filter(passing_tds=True, home=True):
                    hometd+=1
                for p in d.plays.filter(passing_int=True, home=True):
                    homepassint+=1
                for p in d.plays.filter(passing_att=True, home=True):
                    homeatt+=1
                for p in d.plays.filter(passing_tds=True, home=False):
                    awaytd+=1
                for p in d.plays.filter(passing_int=True, home=False):
                    awayint+=1
                for p in d.plays.filter(passing_att=True, home=False):
                    awayatt+=1
            result.append([weekno, yearno, g.home, homeatt, hometd, homepassint])
            result.append([weekno, yearno, g.away, awayatt, awaytd, awayint])
        weekno+=1
        if yearno==2016 and weekno==4: break
    yearno += 1

#data.to_csv("DrivesByYear.csv")

print result

outfile = open('QBtdint3.csv', 'w')
for n in range(len(result)):
    outfile.write(str(result[n]))
    outfile.write('\n')
outfile.close