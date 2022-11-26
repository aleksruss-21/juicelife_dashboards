import requests
import pandas as pd
from service.process import process_metrica
from cfg import config
from loguru import logger


def get_metrika() -> None:
    """Request data from Metrika (Transactions/Revenue"""
    response = requests.get(
        config.yandex_metrika.url, params=config.yandex_metrika.param, headers=config.yandex_metrika.headers
    )
    if response.status_code == 200:
        logger.info("Successfully connected to Metrika")
        result = response.json()["data"]

        dict_data = {}

        for i in range(0, len(result) - 1):

            if result[i]["dimensions"][1]["name"] is None:
                continue
            dict_data[i] = {
                "date": result[i]["dimensions"][0]["name"],
                "campaign_id": result[i]["dimensions"][1]["direct_id"][2:],
                "campaign_name": result[i]["dimensions"][1]["name"],
                "visits": result[i]["metrics"][0],
                "transactions": int(result[i]["metrics"][1]),
                "revenue": result[i]["metrics"][2],
            }

        dict_keys = ["date", "campaign_id", "campaign_name", "visits", "transactions", "revenue"]
        df = pd.DataFrame.from_dict(dict_data, orient="index", columns=dict_keys)

        process_metrica(df)
    else:
        logger.error(f"Error while connecting to Yandex.Metrika. Response {response.status_code}. {response.text}")
