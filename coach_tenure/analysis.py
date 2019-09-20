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
coaches_data['coaches_per_year'] = coaches_data['n_coaches']/coaches_data['n_years']

print(coaches_data)

# graph time
style.use('fivethirtyeight')
flierprops = dict(marker='o', markersize=12, alpha=1, markerfacecolor='#008fd5', markeredgecolor='#008fd5')
ax = coaches_data.boxplot('coaches_per_year', whis=[5, 95],
                          patch_artist=True,
                          flierprops=flierprops)
ax.title._text = ''
ax.xaxis.labels=False

upper_whisker = coaches_data['coaches_per_year'].quantile(0.95)
lower_whisker = coaches_data['coaches_per_year'].quantile(0.05)

# annotate outliers
for row in coaches_data.iterrows():
    if row[1].coaches_per_year > upper_whisker or row[1].coaches_per_year < lower_whisker:
        plt.annotate(row[0], (1.015, row[1].coaches_per_year-0.0044))

plt.tick_params(axis='x', bottom=False, labelbottom=False)
plt.suptitle('Coaches Per Year', ha='right', fontsize='26')
plt.title('1959-2019 Regular Season', loc='left', fontsize='16')

plt.tight_layout()
plt.axhline(y=0, color='black', linewidth=1.3, alpha=.7)
plt.text(x=0.4, y=-0.03,
         s='footballstatsaredumb.wordpress.com',
         fontsize=14, color='xkcd:darkgreen', ha='left')

plt.show()
