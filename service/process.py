import pandas
from storage import database
from datetime import datetime, timedelta


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
    if database.check_exists_dash(dashboard_id, conn):
        for report_date in df["date"].unique():
            database.delete_from_report(report_date, dashboard_id, conn)

    database.upload_direct_from_pandas(df, dashboard_id, conn)


def process_direct_tg(report: str) -> pandas.DataFrame | None:
    if report.split("\n")[1:][0] == "":
        return None
    df = pandas.DataFrame(
        [x.split("\t") for x in report.split("\n")[1:]],
        columns=[
            "date",
            "campaign_name",
            "criterion",
            "impressions",
            "clicks",
            "cost",
            "conversions",
        ],
    )

    col = ["impressions", "clicks", "cost", "conversions"]
    change_minuses(col, df)
    return df


def make_messages(data: pandas.DataFrame, login: str) -> tuple[str, str, str]:
    """Make messages to telegram bot"""

    data = data.dropna(subset=["campaign_name"]).copy()
    data["cost"] = data["cost"].astype("float")
    data[["impressions", "clicks", "conversions"]] = data[["impressions", "clicks", "conversions"]].astype("int")
    # First Message
    yesterday = datetime.strftime(datetime.now() - timedelta(days=1), "%d.%m.%Y")
    message_overall = (
        f"<b>📅 {login} | Сводка за {yesterday}:\n\n</b>"
        f"<b><u>🔸 Итого:</u></b>\n          Показы: {data['impressions'].sum()}\n"
        f"          Клики: {data['clicks'].sum()}\n"
        f"          Расходы: {data['cost'].sum()} ₽\n"
        f"          Конверсий: {data['conversions'].sum()}\n"
    )
    if data["conversions"].sum() > 0:
        message_overall += f"          CPL: {round(data['cost'].sum() / data['conversions'].sum(), 2) } ₽\n"
    # Second Message
    data_campaigns = data.groupby("campaign_name").sum().sort_values(by="cost", ascending=False)

    message_campaigns = ""

    for index, row in data_campaigns.iterrows():
        message_campaigns += f"""<b>▫ {index}</b>
          Показы: {round(row['impressions'])}
          Клики: {round(row['clicks'])}
          Расходы: {round(row['cost'], 2)} ₽\n\n"""

    # Third Message
    data_keywords = data.sort_values(by="cost", ascending=False)

    message_keywords = "<b>Топ-25 условий таргетинга:</b>\n"

    for index, row in data_keywords[:25].iterrows():
        keyword = row['criterion'].split('-')[0].strip()
        if keyword == "":
            keyword = row['criterion']
        message_keywords += f"{keyword} ({row['clicks']}, {row['cost']}₽)\n"

    return message_overall, message_campaigns, message_keywords
