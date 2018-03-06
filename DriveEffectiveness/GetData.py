import pandas as pd
import numpy as np
import nflgame as nfl
from playInfo import *
import sys


# Get a game
def getgames(weekno, yearno):
    return nfl.games(year=yearno, week=weekno)


teamList = []
for team in nfl.teams:
    teamList.append(team[0])
teamList.append("STL")

years = range(2009, 2017)
regSeasonWeeks = range(1, 18)

fullYearData = pd.DataFrame(columns=["rush yds", "rush att", "pass yds", "pass att", "fumbles - passes", "fumbles - runs", "INTs"],
                            index=pd.MultiIndex.from_product([teamList, regSeasonWeeks, years]), data=0)

print fullYearData.index

results = set()
for year in years:
    for week in regSeasonWeeks:
        print "week " + str(year) + "." + str(week)
        for game in getgames(week, year):
            for drive in game.drives:
                team = drive.team
                results.add(drive.result)
                if team == "JAX":
                    team = "JAC"
                for play in str(drive.plays).split(".,"):  # drive.plays is weird, tweaked it to get it to be useful
                    playType = playtype(play)
                    try:
                        if int(playType[1]) > -200:
                            if "pass" in playType[0] or "SACK" in playType[0] or "Pass" in playType[0]:
                                fullYearData.loc[(team, week, year), "pass att"] += 1
                                if playType[1] > -100:
                                    fullYearData.loc[(team, week, year), "pass yds"] += float(playType[1])
                                elif "Fumble" in playType[0]:
                                    fullYearData.loc[(team, week, year), "fumbles - passes"] += 1
                                elif "Int" in playType[0]:
                                    fullYearData.loc[(team, week, year), "INTs"] += 1
                            elif "run" in playType[0] or "Run" in playType[0]:
                                fullYearData.loc[(team, week, year), "rush att"] += 1
                                if playType[1] > -100:
                                    fullYearData.loc[(team, week, year), "rush yds"] += float(playType[1])
                                else:
                                    fullYearData.loc[(team, week, year), "fumbles - runs"] += 1
                            else:
                                print "Other kind of play: " + play
                    except Exception as e:
                        print play + str(playType)
    print results
    sys.exit

fullYearData.to_csv("8years.csv")
