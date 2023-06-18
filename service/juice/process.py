import pandas
from storage.jl_db import upload_daily_direct


def change_minuses(col: list[str], df: pandas.DataFrame) -> None:
    """Replace "--" to 0 in dataframe"""
    for item in col:
        df[item] = df[item].replace(["--"], None)

def process_direct(report: str, account_id: int) -> None:
    """Process data from Direct and upload to database"""

    df = pandas.DataFrame(
        [x.split("\t") for x in report.split("\n")[1:]],
        columns=[
            "date",
            "campaign_id",
            "campaign_name",
            "campaign_type",
            "ad_group_id",
            "ad_group_name",
            "age",
            "targeting_location_id",
            "targeting_location_name",
            "gender",
            "criterion",
            "criterion_id",
            "criterion_type",
            "device",
            "impressions",
            "clicks",
            "cost",
            "bounces",
            "conversions",
        ],
    )

    col = [
        "ad_group_id",
        "criterion_id",
        "impressions",
        "clicks",
        "cost",
        "bounces",
        "conversions",
    ]
    change_minuses(col, df)

    df = df.dropna(subset=["campaign_id"])

    upload_daily_direct(df, account_id)