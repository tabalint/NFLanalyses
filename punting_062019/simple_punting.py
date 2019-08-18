import nfldb
import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.style as style
import math

# fields for punt stats
fields = ['gsis_id', 'play_id', 'punting_yds', 'punting_blk', 'punting_i20',
          'punting_tot', 'punting_touchback', 'punting_yds',
          'puntret_fair', 'puntret_tds', 'puntret_tot',
          'puntret_touchback', 'puntret_yds', 'down', 'yardline', 'yards_to_go', 'pos_team']
punt_fields = [x for x in fields if x not in ['gsis_id', 'play_id', 'down', 'yardline', 'yards_to_go', 'pos_team']]
filename = 'all_punts.csv'


# Do the NFLDB query and save the result to CSV
def save_punt_data():
    print('Getting punt data from NFLDB')
    db = nfldb.connect()
    q = nfldb.Query(db)
    q.game(season_year__ge=2005).game(season_type='Regular')

    all_plays = q.sort('gsis_id').as_plays()
    plays = [{f: l.__getattribute__(f) for f in fields} for l in all_plays]
    punts = [x for x in plays if sum([x.get(n) for n in punt_fields]) > 0]

    # get the yardline out of the yardline object
    for p in punts:
        p['Field Position'] = p.get('yardline')
        p['yardline'] = p.get('yardline')._offset

    print('Saving punt data to CSV')
    df = pd.DataFrame(punts)
    df.to_csv(filename)


def get_punt_data():
    if not os.path.isfile(filename):
        save_punt_data()

    return pd.read_csv(filename)


def process_data():
    # Get the data and process it for punt data
    df = get_punt_data()
    df1 = df[['yardline', 'down']].groupby(['yardline']).agg('count')
    df2 = df[['yardline', 'punting_blk', 'punting_tot',
              'punting_touchback',
              'puntret_fair', 'puntret_tds',
              'puntret_tot']].groupby('yardline').agg('sum')
    full_df = df1.join(df2, how='inner') \
        .join(df[['yardline', 'Field Position']].groupby('yardline').agg('first'), how='inner')

    for x in ['punting_blk', 'punting_touchback', 'puntret_fair', 'puntret_tds', 'puntret_tot']:
        full_df[x] = full_df[x] / full_df['down'] * 100
    # full_df.to_csv('punts.csv')
    return full_df


full_df = process_data()
# Prepare and show the plots
style.use('fivethirtyeight')


def plot_total_punts():
    full_df.plot(y='down', kind='line', legend=False)  # Number of punts in data
    yards = list(range(-50, 20, 5))
    yardlines = [str(nfldb.types.FieldPosition(x)) for x in yards]
    plt.xticks(yards, yardlines)
    plt.xlabel('Yardline')
    plt.yticks(range(0,max(full_df['down']), 200))
    plt.suptitle('Total Punts                                         ', ha='right', fontsize='25')
    plt.title('2005-2018 Regular Season', loc='left', fontsize='16')

    plt.tight_layout()
    plt.axhline(y=0, color='black', linewidth=1.3, alpha=.7)
    plt.text(x=-57, y=-172,
             s='footballstatsaredumb.wordpress.com',
             fontsize=14, color='xkcd:darkgreen', ha='left')

    plt.show()
    # plt.savefig('AllPunts.png')


def plot_punt_details():
    trimmed_df = full_df.loc[-45:10]
    trimmed_df = trimmed_df.rename(columns={'punting_touchback': 'Touchback',
                                            'puntret_fair': 'Fair Catch',
                                            'puntret_tot': 'Returns'})
    trimmed_df['Downed/Out of Bounds'] = 100 - trimmed_df['Touchback'] \
                                             - trimmed_df['Fair Catch'] \
                                             - trimmed_df['Returns'] \
                                             - trimmed_df['puntret_tds'] \
                                             - trimmed_df['punting_blk']
    trimmed_df.plot(y=['Touchback', 'Fair Catch', 'Returns', 'Downed/Out of Bounds'],
                    kind='line')
    # full_df.plot(y=['puntret_tot', 'puntret_fair'], kind='line')  # Fraction of punts that are returned
    yards = list(range(-45, 15,  5))
    yardlines = [str(nfldb.types.FieldPosition(x)) for x in yards]
    plt.xticks(yards, yardlines)
    plt.xlabel('Yardline')
    plt.suptitle('Punt Results - Percentage                    ', ha='right', fontsize='25')
    plt.title('2005-2018 Regular Season', loc='left', fontsize='16')

    plt.tight_layout()
    plt.axhline(y=0, color='black', linewidth=1.3, alpha=.7)
    plt.text(x=-50, y=-14,
             s='footballstatsaredumb.wordpress.com',
             fontsize=14, color='xkcd:darkgreen', ha='left')

    plt.show()
    # plt.savefig('PuntResults.png')


def plot_punt_details_pie():
    punt_df = get_punt_data()
    def punt_result(row):
        if row['punting_blk'] > 0:
            return 'Punt Block'
        elif row['puntret_tds'] > 0:
            return 'Touchdown'
        elif row['punting_touchback'] > 0:
            return 'Touchback'
        elif row['puntret_fair'] > 0:
            return'Fair Catch'
        elif row['puntret_tot'] > 0:
            return 'Return'
        else:
            return 'Downed/Out of Bounds'
    punt_df['Punt Result'] = punt_df.apply(punt_result, axis=1)
    grouped_df = punt_df.groupby('Punt Result').agg('count')['yardline'].rename('Frequency')

    grouped_df.plot.pie(autopct='%2.1f', pctdistance=0.7, labeldistance=1.1,
                        startangle=0, explode=(0.05, 0.05, 0.05, 0.05, 0.05, 0.05))
    plt.axis('equal')
    plt.ylabel('')
    plt.suptitle('Punt Results                                       ', ha='right', fontsize='26')
    plt.title('           2005-2018 Regular Season', loc='left', fontsize='16')

    plt.tight_layout()
    plt.text(x=-2.6, y=-1.2,
             s='footballstatsaredumb.wordpress.com',
             fontsize=14, color='xkcd:darkgreen', ha='left')

    plt.show()
    # plt.savefig('PuntResultsPie.png')


def plot_rare_punts():
    trimmed_df = full_df.copy()
    trimmed_df = trimmed_df.rename(columns={'puntret_tds': 'Touchdowns',
                                            'punting_blk': 'Blocked Punts'})
    trimmed_df.plot(y=['Touchdowns', 'Blocked Punts'],
                    kind='line')
    # full_df.plot(y=['puntret_tot', 'puntret_fair'], kind='line')  # Fraction of punts that are returned
    yards = list(range(-50, 20,  5))
    yardlines = [str(nfldb.types.FieldPosition(x)) for x in yards]
    plt.xticks(yards, yardlines)
    plt.xlabel('Yardline')
    plt.suptitle('Rare Punt Results - Percentage         ', ha='right', fontsize='26')
    plt.title('2005-2018 Regular Season', loc='left', fontsize='16')

    plt.tight_layout()
    plt.axhline(y=0, color='black', linewidth=1.3, alpha=.7)
    plt.text(x=-56, y=-0.75,
             s='footballstatsaredumb.wordpress.com',
             fontsize=14, color='xkcd:darkgreen', ha='left')

    plt.show()
    # plt.savefig('RarePunts.png')


def plot_punt_yardage():
    punts_df = get_punt_data()

    ax = punts_df.boxplot('punting_yds', 'yardline', sym='', whis=[5, 95], patch_artist=True, notch=True)
    ax.title._text = ''
    yards = list(range(-50, 25,  5))
    yardlines = [str(nfldb.types.FieldPosition(x)) for x in yards]
    plt.xticks(list(range(0, 74, 5)), yardlines)
    plt.xlabel('Yardline')

    plt.suptitle('Punt Distances In Air From LOS         ', ha='right', fontsize='26')
    plt.title('2005-2018 Regular Season', loc='left', fontsize='16')

    plt.tight_layout()
    plt.axhline(y=0, color='black', linewidth=1.3, alpha=.7)
    plt.text(x=-6, y=-14,
             s='footballstatsaredumb.wordpress.com',
             fontsize=14, color='xkcd:darkgreen', ha='left')

    plt.show()
    # plt.savefig('PuntYards.png')


def analyze_malone():
    db = nfldb.connect()
    q = nfldb.Query(db)
    q.game(season_year__ge=2005).game(season_type='Regular')
    q.player(full_name="Robert Malone")
    all_plays = q.as_plays()

    plays = [{f: l.__getattribute__(f) for f in fields} for l in all_plays]
    punts = [x for x in plays if sum([x.get(n) for n in punt_fields]) > 0]

    # get the yardline out of the yardline object
    for p in punts:
        p['Field Position'] = p.get('yardline')
        p['yardline'] = p.get('yardline')._offset

    df = pd.DataFrame(punts)
    print(df.head())

    df['punting_yds'].plot(kind='hist', bins=42)
    plt.xlabel('Yards In Air')

    plt.suptitle('Punt Distances In Air From LOS    ', ha='right', fontsize='26')
    plt.title('Robert Malone\'s punts', loc='left', fontsize='16')
    plt.yticks([0,5,10,15,20])

    plt.tight_layout()
    plt.axhline(y=0, color='black', linewidth=1.3, alpha=.7)
    plt.text(x=-15, y=-3,
             s='footballstatsaredumb.wordpress.com',
             fontsize=14, color='xkcd:darkgreen', ha='left')
    plt.show()


def plot_punt_yardage_histo():
    punts_df = get_punt_data()

    ax = punts_df['punting_yds'][(punts_df['yardline'] > -46) &
                                 (punts_df['yardline'] < 11) &
                                 (punts_df['punting_yds'] > 1)].plot(kind='hist', bins=81)

    plt.suptitle('Punt Distances In Air From LOS ', ha='right', fontsize='25')
    plt.title('2005-2018 Regular Season', loc='left', fontsize='16')

    plt.tight_layout()
    plt.axhline(y=0, color='black', linewidth=5.8, alpha=.7)
    plt.text(x=-18, y=-100,
             s='footballstatsaredumb.wordpress.com',
             fontsize=14, color='xkcd:darkgreen', ha='left')

    plt.show()
    # plt.savefig('PuntYardsHisto.png')


def plot_punt_results_by_distance():
    df = get_punt_data()
    df = df[(df['yardline'] > -46) &
            (df['yardline'] < 11) &
            (df['punting_yds'] > 1)]
    df1 = df[['punting_yds', 'down']].groupby(['punting_yds']).agg('count')
    df2 = df[['punting_yds', 'punting_blk', 'punting_tot',
              'punting_touchback',
              'puntret_fair', 'puntret_tds',
              'puntret_tot']].groupby('punting_yds').agg('sum')
    df3 = df1.join(df2, how='inner') \
        .join(df[['punting_yds', 'Field Position']].groupby('punting_yds').agg('first'), how='inner')

    for x in ['punting_blk', 'punting_touchback', 'puntret_fair', 'puntret_tds', 'puntret_tot']:
        df3[x] = df3[x] / df3['down'] * 100

    trimmed_df = df3.rename(columns={'punting_touchback': 'Touchback',
                                            'puntret_fair': 'Fair Catch',
                                            'puntret_tot': 'Returns'})
    trimmed_df['Downed/Out of Bounds'] = 100 - trimmed_df['Touchback'] \
                                             - trimmed_df['Fair Catch'] \
                                             - trimmed_df['Returns'] \
                                             - trimmed_df['puntret_tds'] \
                                             - trimmed_df['punting_blk']

    trimmed_df.loc[20:70]\
              .plot(y=['Touchback', 'Fair Catch', 'Returns', 'Downed/Out of Bounds'],
                    kind='line')

    plt.xlabel('Punt Distance')
    plt.suptitle('Punt Results By Distance - Percentage ', ha='right', fontsize='25')
    plt.title('2005-2018 Regular Season', loc='left', fontsize='16')

    plt.tight_layout()
    plt.axhline(y=0, color='black', linewidth=1.3, alpha=.7)
    plt.text(x=16, y=-20,
             s='footballstatsaredumb.wordpress.com',
             fontsize=14, color='xkcd:darkgreen', ha='left')

    plt.show()


def plot_punt_return_yds():
    df = get_punt_data()
    df[df['puntret_tot'] > 0]['puntret_yds'].plot(kind='hist', bins=114, cumulative=True, density=True)

    plt.suptitle('Punt Return Distances                   ', ha='right', fontsize='25')
    plt.title('2005-2018 Regular Season', loc='left', fontsize='16')
    plt.ylabel('Cumulative Frequency')

    plt.tight_layout()
    plt.axhline(y=0, color='black', linewidth=5.8, alpha=.7)
    plt.text(x=-39, y=-0.1,
             s='footballstatsaredumb.wordpress.com',
             fontsize=14, color='xkcd:darkgreen', ha='left')

    plt.show()


plot_punt_return_yds()
