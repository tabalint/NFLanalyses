import nfldb
import pandas as pd
import os

FILENAME = 'all_drives.csv'


# Do the NFLDB query and save the result to CSV
# For now this just gets basic drive data - starting position and points earned
def save_drive_data():
    print('Getting drive data from NFLDB')
    db = nfldb.connect()
    q = nfldb.Query(db)
    q.game(season_year__ge=2005).game(season_type='Regular')

    # Create a list of (starting position string, starting position abs value, points earned)
    drives = [(str(x.start_field), x.start_field._offset, sum(y.points for y in x.plays))
              for x in q.as_drives()
              if x.start_field._offset is not None]

    print('Saving drive data to CSV')
    df = pd.DataFrame(drives)
    df.to_csv(FILENAME)


def get_drive_data():
    if not os.path.isfile(FILENAME):
        save_drive_data()

    return pd.read_csv(FILENAME)


save_drive_data()