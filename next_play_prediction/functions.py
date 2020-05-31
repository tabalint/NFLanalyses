from google.cloud import bigquery
import pandas as pd
import os

FILENAME = 'data.csv'


# Simply returns a bigquery client - helper function to remove the need to import bigquery everywhere, and keep code DRY
def get_bq_client():
    return bigquery.Client.from_service_account_json("C:\\pynfldata.json")


def get_data():
    if os.path.isfile(FILENAME):
        return pd.read_csv(FILENAME, index_col=0)
    else:
        client = get_bq_client()

        sql = """SELECT *
                   FROM `pynfldata.drives.2019_ml_input_materialized`
              """

        df = client.query(sql).to_dataframe()
        df.to_csv(FILENAME)
        return pd.read_csv(FILENAME)
