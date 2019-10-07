# fixme NFLDB data is wrong - build new data stream from NFL.com
import drive_value_081419.basic_functions as bf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.style as style
import nfldb
import math


full_df = bf.get_drive_data()[['yard_offset', 'points']]
# Prepare and show the plots
style.use('fivethirtyeight')


def plot_first_order_drive_result():
    df1 = full_df.groupby(['yard_offset'], axis=0).points.agg(['mean', np.std, 'count'])
    df1['points'] = df1['mean']
    df1['err_fac'] = df1['count'].apply(lambda x: math.sqrt(x))
    df1['error'] = df1['std']/df1['err_fac']

    print(df1)

    df1.plot(y='points', kind='line', legend=False)

    # x-axis
    yards = list(range(-50, 50, 5))
    yardlines = [str(nfldb.types.FieldPosition(x)) for x in yards]
    plt.xticks(yards, yardlines, rotation=45)  # rotate since we're using all 100 yards
    plt.xlabel('Yardline')

    # y-axis
    plt.ylabel('Points')
    plt.ylim([0,8])
    # create a shaded error region
    plt.fill_between(df1.index, df1['points']-df1['error'], df1['points']+df1['error'], alpha=0.35)

    # titles
    plt.suptitle('Drive Expected Value                        ', ha='right', fontsize='25')
    plt.title('2005-2018 Regular Season', loc='left', fontsize='16')

    # general formatting
    plt.tight_layout()
    plt.axhline(y=0, color='black', linewidth=1.3, alpha=.7)
    plt.text(x=-57, y=-172,
             s='footballstatsaredumb.wordpress.com',
             fontsize=14, color='xkcd:darkgreen', ha='left')

    plt.show()
    plt.savefig('first_order.png')


plot_first_order_drive_result()