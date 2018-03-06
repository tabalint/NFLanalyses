import nflgame as N
import pandas as pd

data = pd.DataFrame(0, index=[1], columns=['year', 'name', 'thisAtt', 'thisYds', 'nextAtt', 'nextYds'])
garbage=[]

yearno=2009
while yearno<2015:
    gamesthis = N.games(yearno, kind='REG')
    gamesnext = N.games(yearno+1, kind='REG')
    playerstatsthis = N.combine_game_stats(gamesthis)
    #playerstatsnext = N.combine_game_stats(gamesnext)
    #playersthis = N.combine(gamesthis)
    playersnext = N.combine(gamesnext)
    
    for p in playerstatsthis.rushing():
        player = playersnext.name(str(p))
        try:
            if p.rushing_att > 25 and player.rushing_att > 25:
                data = data.append(dict(year=yearno, name=p, thisAtt=p.rushing_att, thisYds=p.rushing_yds, nextAtt=player.rushing_att, nextYds=player.rushing_yds), ignore_index=True)
                #print(str(p), p.rushing_att, p.rushing_yds, player.rushing_att, player.rushing_yds)
        except:
            garbage.append(str(p))
    yearno+=1

data.to_csv('curse.csv')
print("Done!")
#for p in playerstats2014.rushing():
#    if p.rushing_att > 350: 
#        print(p)
#        player = players2015.name(str(p))
#        print(player.rushing_att)