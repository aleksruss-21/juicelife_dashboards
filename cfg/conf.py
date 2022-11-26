from loguru import logger
from datetime import date

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB", compression="zip")


class Config:
    def __init__(self):
        self.yandex_direct = self.YandexDirect()
        self.database = self.Database()

    class YandexDirect:
        def __init__(self):
            self.TOKEN_YANDEX = "token"
            self.url_direct_ads = "https://api.direct.yandex.com/json/v5/ads"
            self.url_direct_report = "https://api.direct.yandex.com/json/v5/reports"
            self.url_direct_clients = "https://api.direct.yandex.com/json/v5/clients"

            self.oauth_url = "https://oauth.yandex.ru/token"

            # Headers for direct api request
            self.direct_headers = {
                "Authorization": self.TOKEN_YANDEX,
                "Accept-Language": "en",
                "skipReportHeader": "true",
                "skipReportSummary": "true",
                "returnMoneyInMicros": "false",
            }

            # JSON for report direct api request
            self.direct_params_report = {
                "params": {
                    "SelectionCriteria": {
                        "DateFrom": "2022-09-26",
                        "DateTo": "2022-11-24",
                        "Filter": [
                            {
                                "Field": "Clicks",
                                "Operator": "GREATER_THAN",
                                "Values": ["0"],
                            }
                        ],
                    },
                    "Goals": ["185562538", "103409737", "135355996"],
                    "AttributionModels": ["LSC"],
                    "FieldNames": [
                        "Date",
                        "CampaignId",
                        "CampaignName",
                        "Impressions",
                        "Clicks",
                        "Cost",
                        "Conversions",
                    ],
                    "ReportName": f"Report_{date.today()}_OLDV5",
                    "ReportType": "CUSTOM_REPORT",
                    "DateRangeType": "CUSTOM_DATE",
                    "Format": "TSV",
                    "IncludeVAT": "NO",
                }
            }

    class Database:
        def __init__(self):
            self.dbname = "juicelife_dashboards"
            self.user = "admin_juicelife"
            self.password = "mypassword"
            self.host = "0.0.0.0"
            self.async_conn_query = f"dbname={self.dbname} user={self.user} host={self.host} password={self.password}"


def get_instance():
    """Get instance of Config"""
    return Config()
