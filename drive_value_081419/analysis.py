from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession, SQLContext
import pyspark.sql.functions as F
import matplotlib.pyplot as plt
from pynfldata.data_tools import nfl_types
from scipy.stats import linregress
import os
import pandas as pd

PD_FILENAME = 'results_pd_df.csv'


def calculate_average_ev_by_yardline():
    conf = SparkConf().setAppName('Drive Analysis').setMaster('local[4]')
    sc = SparkContext(conf=conf)
    spark = SparkSession.builder.master("local").appName("Drive Analysis").getOrCreate()
    sql_context = SQLContext(sc)

    # get pq data, from https://github.com/tabalint/pynfldata/tree/master/pynfldata/drives_data
    drives_data = sql_context.read.parquet('drives.pq')

    # unpack drives column of arrays into raw column
    drive_df = drives_data.select('game_id', F.explode('drives').alias('drive')).select(['game_id', 'drive.*'])

    # dispose of rows without drive_start - typically fake drives that are just a kickoff
    drive_df = drive_df.filter(~F.isnull(drive_df.drive_start))
    sql_context.registerDataFrameAsTable(drive_df, 'drives')

    # Correctly account for turnover points
    test_df = sql_context.sql("""SELECT *,
                              CASE WHEN drive_points IS NULL THEN 0
                                   WHEN drive_pos_team == drive_scoring_team THEN drive_points
                                   WHEN drive_pos_team != drive_scoring_team THEN (-1)*drive_points
                                   ELSE drive_points
                               END AS realpoints
                              FROM drives""")

    # groupby starting yardline, get measures of points
    results_df = test_df.groupBy('drive_start')\
                        .agg(F.stddev('realpoints').alias('stddev'),
                             F.mean('realpoints').alias('points'),
                             F.count('realpoints').alias('count')).sort('drive_start')
    results_df = results_df.withColumn('error', (F.col('stddev')/F.sqrt(F.col('count'))))

    return results_df.toPandas()


def get_avg_ev_pd_df():
    if not os.path.exists(PD_FILENAME):
        results_pd_df = calculate_average_ev_by_yardline()
        results_pd_df.to_csv(PD_FILENAME)
    else:
        results_pd_df = pd.read_csv(PD_FILENAME)
    return results_pd_df


def full_drive_ev():
    results_pd_df = get_avg_ev_pd_df()
    results_pd_df.plot(x='drive_start', y='points', kind='line', legend=False)

    # x-axis
    yards = list(range(-50, 50, 5))
    yardlines = [str(nfl_types.Yardline(x)) for x in yards]
    plt.xticks(yards, yardlines, rotation=75)  # rotate since we're using all 100 yards
    plt.xlabel('Yardline', fontsize=16)

    # y-axis
    plt.ylabel('Points', fontsize=16)
    plt.ylim([0, 7])
    # create a shaded error region
    plt.fill_between(results_pd_df.drive_start,
                     results_pd_df['points'] - results_pd_df['error'],
                     results_pd_df['points'] + results_pd_df['error'], alpha=0.35)

    # titles
    plt.suptitle('Drive Expected Value                         ', ha='right', fontsize='25')
    plt.title('2009-2018 Regular Season', loc='left', fontsize='16')

    # general formatting
    plt.tight_layout()
    plt.axvline(x=0, color='black', linewidth=0.5, alpha=0.5)  # midfield marker
    plt.axhline(y=0, color='black', linewidth=1.3, alpha=.7)  # to make the y=0 axis pop
    plt.text(x=-57, y=-1.5,
             s='footballstatsaredumb.wordpress.com',
             fontsize=14, color='xkcd:darkgreen', ha='left')

    plt.show()


def fit_linear_and_plot():
    results_pd_df = get_avg_ev_pd_df()
    results_pd_df = results_pd_df[results_pd_df['drive_start'] <= 0]  # Limit it to OWN side of field

    # Calculate best-fit line and statistics
    (_, x), (_, y) = results_pd_df[['drive_start', 'points']].iteritems()
    slope, intercept, r, p, stderr = linregress(x, y)

    results_pd_df.plot(x='drive_start', y='points', kind='line', legend=False)

    # x-axis
    yards = list(range(-50, 5, 5))
    yardlines = [str(nfl_types.Yardline(x)) for x in yards]
    plt.xticks(yards, yardlines, rotation=75)  # rotate since we're using all 100 yards
    plt.xlabel('Yardline', fontsize=16)

    # y-axis
    plt.ylabel('Points', fontsize=16)
    plt.ylim([0, 3])
    # create a shaded error region
    plt.fill_between(results_pd_df.drive_start,
                     results_pd_df['points'] - results_pd_df['error'],
                     results_pd_df['points'] + results_pd_df['error'], alpha=0.35)

    # plot best-fit line
    plt.plot([-50, 0], [intercept-50*slope, intercept], color='k', linestyle='-', linewidth=2)
    plt.annotate('y={:.3}x+{:.3}\nr={:.3}'.format(slope, intercept, r), (-20, 2.2), fontsize=16)

    # titles
    plt.suptitle('Drive Expected Value (OWN side)   ', ha='right', fontsize='25')
    plt.title('2009-2018 Regular Season', loc='left', fontsize='16')

    # general formatting
    plt.tight_layout()
    plt.axvline(x=0, color='black', linewidth=0.5, alpha=0.5)  # midfield marker
    plt.axhline(y=0, color='black', linewidth=1.3, alpha=.7)  # to make the y=0 axis pop
    plt.text(x=-54, y=-0.75,
             s='footballstatsaredumb.wordpress.com',
             fontsize=14, color='xkcd:darkgreen', ha='left')

    plt.show()


full_drive_ev()
fit_linear_and_plot()
