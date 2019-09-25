import pandas as pd
from utilities import team_functions as tf
from matplotlib import pyplot as plt
import matplotlib.style as style


def calculate_n_coaches():
    # data from https://github.com/tabalint/pynfldata/tree/master/pynfldata/coaches_data
    data_df = pd.read_csv('coaches.csv')
    data_df = tf.make_teams_continuous(data_df, 'abbr', 'season')

    coaches_df = data_df.set_index(['abbr', 'season']).sort_index()

    # Add a marker to note coach continuity
    coaches_df['marker'] = (coaches_df['coachNFLID'] != coaches_df['coachNFLID'].shift()).cumsum()

    # Now do the groupby
    result = coaches_df.groupby(['abbr']).agg(n_coaches=('marker', pd.Series.nunique),
                                              n_years=('marker', 'count'))

    return result


coaches_data = calculate_n_coaches()
coaches_data['years_per_coach'] = coaches_data['n_years']/coaches_data['n_coaches']

style.use('fivethirtyeight')


# Creates a vertical boxplot of years/coach data
def coach_tenure_boxplot(coach_df: pd.DataFrame):
    flier_props = dict(marker='o', markersize=12, alpha=1, markerfacecolor='#008fd5', markeredgecolor='#008fd5')
    ax = coach_df.boxplot('years_per_coach', whis=[5, 95],
                          patch_artist=True,
                          flierprops=flier_props)
    ax.title._text = ''
    ax.xaxis.labels = False

    # annotate outliers - first calculate the ends of the whiskers
    upper_whisker = coach_df['years_per_coach'].quantile(0.95)
    lower_whisker = coach_df['years_per_coach'].quantile(0.05)

    # using that, put labels on the outliers
    for row in coach_df.iterrows():
        if row[1].years_per_coach > upper_whisker or row[1].years_per_coach < lower_whisker:
            plt.annotate(row[0], (1.015, row[1].years_per_coach-0.17))

    # x-axis and titles
    plt.tick_params(axis='x', bottom=False, labelbottom=False)
    plt.suptitle('   Average Coach Tenure', ha='right', fontsize='24')
    plt.title('1969-2019 Regular Season', loc='left', fontsize='16')

    plt.tight_layout()
    plt.axhline(y=0, color='black', linewidth=1.3, alpha=.7)
    plt.text(x=0.43, y=-1,
             s='footballstatsaredumb.wordpress.com',
             fontsize=14, color='xkcd:darkgreen', ha='left')

    plt.show()


# Calculate distribution's statistics and z-score, print
def calculate_stats(coaches_df: pd.DataFrame):
    std = coaches_df['years_per_coach'].std()
    avg = coaches_df['years_per_coach'].mean()
    median = coaches_df['years_per_coach'].median()
    print("mean={mean}, median={median}, std={std}".format(mean=avg, median=median, std=std))
    coaches_df['z_score'] = (coaches_df['years_per_coach'] - avg)/std

    print(coaches_df.sort_values(['z_score']))


coach_tenure_boxplot(coaches_data)
calculate_stats(coaches_data)
