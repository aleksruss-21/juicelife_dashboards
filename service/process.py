import pandas
from storage import database


def process_direct(report: str, dashboard_id: int) -> None:
    """Process data from Direct and upload to database"""
    df = pandas.DataFrame(
        [x.split("\t") for x in report.split("\n")[1:]],
        columns=[x for x in report.split("\n")[0].split("\t")],
    )

    for index, row in df.iterrows():
        arr = []
        for data in row:
            if data == "--":
                data = 0
            if isinstance(data, str):
                data = data.replace("'", "")
            if row["CampaignId"] is not None:
                arr.append(f"'{data}'")

        report_row = ",".join(arr)
        if arr:
            database.upload_direct(report_row, dashboard_id)
