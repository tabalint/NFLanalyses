def playType(fields):
    pType = set()
    if 'rushing_att' in fields: pType.add(('rushing_att', 'rushing_yds'))
    if 'passing_att' in fields: pType.add(('passing_att', 'passing_yds'))
    if 'kicking_tot' in fields: pType.add(('kicking_tot', ''))
    if 'punting_tot' in fields: pType.add(('punting_tot', ''))
    if 'kicking_xpa' in fields: pType.add(('kicking_xpa', ''))
    if 'kicking_fga' in fields: pType.add(('kicking_fga', ''))
    if 'passing_sk' in fields: pType.add(('passing_sk', ''))
    if 'defense_puntblk' in fields: pType.add(('defense_puntblk', ''))
    return pType


import nfldb
import pandas as pd

rowsList = []

db = nfldb.connect()
q = nfldb.Query(db)
q.game(season_year=2016, season_type='Regular')
drives = q.drive().sort(('start_time', 'asc')).as_drives()
print "got drives " + str(len(drives))
i=0
j=0
for d in drives:
    i+=1
    g = nfldb.Game.from_id(db, d.gsis_id)
    for p in d.plays:
        j+=1
        if p.rushing_att > 0 or p.passing_att>0:
            score = g.score_at_time(p.time)
            if(p.pos_team == g.home_team):
                ptdiff = score[0]-score[1]
            else:
                ptdiff = score[1]-score[0]
            thisDict = {'team': d.pos_team, 'week': g.week, 'year': g.season_year, 'drive': i, 'play': j,
                        'down': p.down, 'togo': p.yards_to_go, 'quarter': p.time.phase.name, 'ptdiff': ptdiff,
                        'rush yds': p.rushing_yds, 'rush att': p.rushing_att,
                        'pass yds': p.passing_yds, 'pass att': p.passing_att}
            rowsList.append(thisDict)

answer = pd.DataFrame(rowsList)
print "meh"
answer.to_csv('db2016.csv')

    # for p in d.plays:
    #
    #     playFields = [list(x.fields) for x in p.play_players]
    #     playFields = set([item for sublist in playFields for item in sublist])
    #
    #     # p.down is only not 1-4 when it's a timeout
    #     # there are no plays with len over 1. plays with len 0 are penalties
    #     pstats = playType(playFields)
    #     if len(pstats) != 1:
    #
    #         if not ('PENALTY' in str(p) or 'Penalty' in str(p)) and p.down > 0:
    #             print '\n' + str(p) + '\t\t' + str(playFields)
    #         # Else it's a timeout or end of quarter
    #     else:
    #         g = nfldb.Game.from_id(db, p.gsis_id)
    #         score = g.score_at_time(p.time)
    #         if(p.pos_team == g.home_team):
    #             ptdiff = score[0]-score[1]
    #         else:
    #             ptdiff = score[1]-score[0]
    #         actualPlayType = playType(playFields).pop()
    #         print(p.pos_team, str(p.yardline), str(p.time), actualPlayType[0], score, ptdiff)
    #         if actualPlayType[1] != '':
    #             print getattr([i for i in p.play_players if actualPlayType[0] in i.fields][0], actualPlayType[1])
            #print actualPlayType, playFields
    #break # for one drive
