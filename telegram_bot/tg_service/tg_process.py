import pandas
from telegram_bot.tg_storage import tg_app_database as database
from datetime import datetime, timedelta
from loguru import logger


def change_minuses(col: list[str], df: pandas.DataFrame) -> None:
    """Replace "--" to 0 in dataframe"""
    for item in col:
        df[item] = df[item].replace(["--"], 0)


def process_direct_tg(report: str, goals: bool) -> pandas.DataFrame | None:
    if report.split("\n")[1:][0] == "":
        return None
    columns = ["date", "campaign_name", "criterion", "impressions", "clicks", "cost"]
    col = ["impressions", "clicks", "cost"]
    if goals is True:
        columns.append("conversions")
        col.append("conversions")

    df = pandas.DataFrame(
        [x.split("\t") for x in report.split("\n")[1:]],
        columns=columns,
    )

    change_minuses(col, df)
    return df


def make_messages(data: pandas.DataFrame, login: str, goals: bool) -> list:
    """Make messages to telegram bot"""

    data = data.dropna(subset=["campaign_name"]).copy()
    data["cost"] = data["cost"].astype("float")
    if goals is True:
        data[["impressions", "clicks", "conversions"]] = data[["impressions", "clicks", "conversions"]].astype("int")
    else:
        data[["impressions", "clicks"]] = data[["impressions", "clicks"]].astype("int")

    msg = []

    # First Message
    yesterday = datetime.strftime(datetime.now() - timedelta(days=1), "%d.%m.%Y")
    message_overall = (
        f"<b>📅 {login} | Сводка за {yesterday}:\n\n</b>"
        f"<b><u>🔸 Итого:</u></b>\n          Показы: {data['impressions'].sum()}\n"
        f"          Клики: {data['clicks'].sum()}\n"
        f"          Расходы: {round(data['cost'].sum(), 2)} ₽\n"
    )
    if goals is True:
        message_overall += f"          Конверсий: {data['conversions'].sum()}\n"
        if data["conversions"].sum() > 0:
            message_overall += f"          CPL: {round(data['cost'].sum() / data['conversions'].sum(), 2) } ₽\n"

    msg.append(message_overall)
    # Second Message
    data_campaigns = data.groupby("campaign_name").sum().sort_values(by="cost", ascending=False)

    message_campaigns = ""

    for index, row in data_campaigns.iterrows():
        message_campaigns += f"""<b>▫ {index}</b>
          Показы: {round(row['impressions'])}
          Клики: {round(row['clicks'])}
          Расходы: {round(row['cost'], 2)} ₽\n\n"""
        if len(message_campaigns) > 2600:
            msg.append(message_campaigns)
            message_campaigns = ""

    if message_campaigns != "":
        msg.append(message_campaigns)

    # Third Message
    data_keywords = data.sort_values(by="cost", ascending=False)

    message_keywords = "<b>Топ-25 условий таргетинга:</b>\n"

    for index, row in data_keywords[:25].iterrows():
        keyword = row["criterion"].split("-")[0].strip()
        if keyword == "":
            keyword = row["criterion"]
        message_keywords += f"{keyword} ({row['clicks']}, {row['cost']}₽)\n"
        if len(message_keywords) > 2600:
            msg.append(message_keywords)
            message_keywords = ""
    if message_keywords != "":
        msg.append(message_keywords)
    return msg
