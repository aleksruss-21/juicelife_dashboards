import pandas
from storage import database


def process_direct(report: str) -> None:
    """Process data from Direct and upload to database"""
    df = pandas.DataFrame(
        [x.split(",") for x in report.split("\n")[1:]],
        columns=[x for x in report.split("\n")[0].split(",")],
    )

    for index, row in df.iterrows():
        arr = []
        for data in row:
            if data == "--":
                data = 0
            if row["CampaignId"] is not None:
                arr.append(f"'{data}'")

        report_row = ",".join(arr)
        if arr:
            database.upload_direct(report_row)


def process_metrica(report: pandas.DataFrame) -> None:
    """Process data from Metrika and upload to database"""
    for index, row in report.iterrows():
        arr = [f"'{row['date']}'", f"'{row['campaign_id']}'", f"'{row['campaign_name']}'", f"'{row['transactions']}'", f"'{row['revenue']}'"]
        database.upload_metrika(",".join(arr))
