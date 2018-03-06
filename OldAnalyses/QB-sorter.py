import nflgame as N
import pandas as pd

games = N.games(2009, week=1)

players = N.combine_game_stats(games)
i=0
plist = players.passing().sort('passing_yds')

clegames = N.games(2009, week=1, home='CLE', away='CLE')
cleplayers = N.combine_game_stats(clegames)
cleplayers.filter(home="CLE",away="CLE",passing_att__gt=5)
clelist = cleplayers.passing().sort('passing_yds')
for c in clelist:
    print c
assert False
for p in plist:
    i+=1
    msg = '%s (%s): %d passes for %d yards and %d TDs'
    if p.team == "CLE":
        print '%d out of %d' %(i,len(plist))
    print msg % (p, p.team, p.passing_att, p.passing_yds, p.passing_tds)

data = pd.DataFrame(0, index=[1], columns=['year', 'name', 'thisAtt', 'thisYds', 'nextAtt', 'nextYds'])
garbage=[]

yearno=2009
while yearno<2016:
    weekno = 1
    while weekno<18:
        assert False