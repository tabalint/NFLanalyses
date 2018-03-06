import nflgame as N
import pandas as pd



data = pd.DataFrame(0, index=[1], columns=['year', 'week', 'name', 'thisAtt'])
garbage=[]

yearno=2009
while yearno<2016:
    weekno = 1
    while weekno<18:
        games = N.games(yearno, week=weekno)
        players = N.combine_game_stats(games)
        plist = players.passing().sort('passing_att')
        for p in plist:
            data = data.append(dict(year=yearno, week=weekno, name=p, thisAtt=p.passing_att), ignore_index=True)
        weekno+=1
    yearno+=1

data.to_csv('passingAttempts.csv')
print("Done!")