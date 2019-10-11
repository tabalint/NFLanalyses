from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession, SQLContext
import pyspark.sql.functions as F
import matplotlib.pyplot as plt
from pynfldata.data_tools import nfl_types


def full_drive_ev():
    conf = SparkConf().setAppName('Drive Analysis').setMaster('local[4]')
    sc = SparkContext(conf=conf)
    spark = SparkSession.builder.master("local").appName("Drive Analysis").getOrCreate()
    sqlContext = SQLContext(sc)

    # get pq data, from https://github.com/tabalint/pynfldata/tree/master/pynfldata/drives_data
    drives_data = sqlContext.read.parquet('drives.pq')

    # unpack drives column of arrays into raw column
    drive_df = drives_data.select(F.explode('drives').alias('drive')).select('drive.*')

    # dispose of rows without drive_start - typically fake drives that are just a kickoff
    drive_df = drive_df.filter(~F.isnull(drive_df.drive_start))

    # groupby starting yardline, get measures of points
    results_df = drive_df.select(['drive_points', 'drive_start']).fillna(0)\
                         .groupBy('drive_start')\
                         .agg(F.stddev('drive_points').alias('stddev'),
                              F.mean('drive_points').alias('points'),
                              F.count('drive_points').alias('count')).sort('drive_start')
    results_df = results_df.withColumn('error', (F.col('stddev')/F.sqrt(F.col('count'))))

    results_pd_df = results_df.toPandas()
    results_pd_df.plot(x='drive_start', y='points', kind='line', legend=False)

    # x-axis
    yards = list(range(-50, 50, 5))
    yardlines = [str(nfl_types.Yardline(x)) for x in yards]
    plt.xticks(yards, yardlines, rotation=45)  # rotate since we're using all 100 yards
    plt.xlabel('Yardline')

    # y-axis
    plt.ylabel('Points')
    plt.ylim([0, 7])
    # create a shaded error region
    plt.fill_between(results_pd_df.drive_start,
                     results_pd_df['points'] - results_pd_df['error'],
                     results_pd_df['points'] + results_pd_df['error'], alpha=0.35)

    # titles
    plt.suptitle('Drive Expected Value                           ', ha='right', fontsize='25')
    plt.title('2009-2018 Regular Season', loc='left', fontsize='16')

    # general formatting
    plt.tight_layout()
    plt.axvline(x=0, color='black', linewidth=0.5, alpha=0.5)  # midfield marker
    plt.axhline(y=0, color='black', linewidth=1.3, alpha=.7)  # to make the y=0 axis pop
    plt.text(x=-57, y=-1.5,
             s='footballstatsaredumb.wordpress.com',
             fontsize=14, color='xkcd:darkgreen', ha='left')

    plt.show()
    plt.savefig('eval_basic.png')
