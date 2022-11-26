from datetime import date
import requests

URL_DIRECT_ADS = "https://api.direct.yandex.com/json/v5/ads"
URL_DIRECT_REPORTS = "https://api.direct.yandex.com/json/v5/reports"
URL_DIRECT_CLIENTS = "https://api.direct.yandex.com/json/v5/clients"
URL_OAUTH = "https://oauth.yandex.ru/token"


def get_daily_data_request(token: str, dashboard_id: int) -> requests.Response:
    """Request to Yandex.Direct API to get daily data"""
    direct_headers = {
        "Authorization": token,
        "Accept-Language": "en",
        "skipReportHeader": "true",
        "skipReportSummary": "true",
        "returnMoneyInMicros": "false",
    }

    direct_params = {
        "params": {
            "SelectionCriteria": {
                "Filter": [
                    {
                        "Field": "Clicks",
                        "Operator": "GREATER_THAN",
                        "Values": ["0"],
                    }
                ],
            },
            # "AttributionModels": ["LSC"],
            "FieldNames": [
                "Date",
                "CampaignId",
                "CampaignName",
                "Criterion",
                "Impressions",
                "Clicks",
                "Cost",
                # "Conversions",
            ],
            "ReportName": f"Report_{date.today()}_{dashboard_id}_test",
            "ReportType": "CUSTOM_REPORT",
            "DateRangeType": "YESTERDAY",
            "Format": "TSV",
            "IncludeVAT": "NO",
        }
    }

    response_report = requests.get(url=URL_DIRECT_REPORTS, headers=direct_headers, json=direct_params)
    return response_report
