import pandas
from storage import database

from datetime import date, timedelta


def iterate_df(df: pandas.DataFrame, dashboard_id: int, is_yesterday: bool) -> None:
    """Iterate DF and send to database module to upload row"""
    for index, row in df.iterrows():
        arr = []
        for data in row:
            if data == "--":
                data = 0
            if isinstance(data, str):
                data = data.replace("'", "")
            if row["CampaignId"] is not None:
                arr.append(f"'{data}'")

        report_row = "|||".join(arr)
        if arr:
            database.upload_direct(report_row, dashboard_id, is_yesterday)


def process_direct(report: str, dashboard_id: int) -> None:
    """Process data from Direct and upload to database"""
    df = pandas.DataFrame(
        [x.split("\t") for x in report.split("\n")[1:]],
        columns=[x for x in report.split("\n")[0].split("\t")],
    )

    df_yesterday = df[df["Date"] == str(date.today() - timedelta(days=1))]
    df_else = df[df["Date"] != str(date.today() - timedelta(days=1))]

    iterate_df(df_yesterday, dashboard_id, True)
    iterate_df(df_else, dashboard_id, False)
