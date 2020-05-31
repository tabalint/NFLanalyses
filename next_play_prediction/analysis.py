from functions import get_data
from matplotlib import pyplot as plt
import matplotlib.style as style
import tensorflow as tf

style.use('fivethirtyeight')


def build_dataframe():
    df = get_data()
    df = df.drop(['scoring_drive', 'final_outcome', 'quarter', 'game_id', 'play_id'], axis=1)
    df['play_type'] = df['play_type'].astype('category')
    df['last_play_type'] = df['last_play_type'].astype('category')
    df['down'] = df['down'].astype('category')
    df['play_in_drive'] = df['play_in_drive'].astype('category')

    df['score_diff'] = df['current_pos_score'] - df['current_opp_score']
    df = df.drop(['current_pos_score', 'current_opp_score'], axis=1)

    return df


def preliminary_analysis(df):
    df_desc = df.describe()
    for col in df_desc:
        print(df_desc[col])

    df_corr = df.corr()
    print(df_corr)

    df['play_type'].hist()
    plt.show()

    df['last_play_type'].hist()
    plt.show()

    df['down'].hist(bins=9)
    plt.show()

    df['yards'].hist(bins=range(-20, 51, 2))
    plt.show()

    df['last_play_yards'].hist(bins=range(-20, 51, 2))
    plt.show()

    df['yards_to_go'].hist(bins=range(0, 31, 1))
    plt.show()

    df['yard_int'].hist(bins=range(0, 101, 2))
    plt.show()

    df['play_in_drive'].hist(bins=range(0, 21, 1))
    plt.show()

    df['score_diff'].hist(bins=range(-30, 31, 2))
    plt.show()

    df['time_remaining_in_game'].hist()
    plt.show()

    df['time_remaining_til_break'].hist()
    plt.show()


def main():
    data_df = build_dataframe()
    preliminary_analysis(data_df)


if __name__ == '__main__':
    main()