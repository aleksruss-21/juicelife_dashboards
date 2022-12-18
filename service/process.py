import pandas
from storage import database


def change_minuses(col: list[str], df: pandas.DataFrame) -> None:
    """Replace "--" to 0 in dataframe"""
    for item in col:
        df[item] = df[item].replace(["--"], 0)


def process_direct(report: str, dashboard_id: int) -> None:
    """Process data from Direct and upload to database"""

    conn = database.create_instance()

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

    col = ["ad_group_id", "criterion_id", "impressions", "clicks", "cost", "bounces", "conversions"]
    change_minuses(col, df)

    df = df.dropna(subset=["campaign_id"])

    for report_date in df["date"].unique():
        database.delete_from_report(report_date, dashboard_id, conn)

    database.upload_direct_from_pandas(df, dashboard_id, conn)
