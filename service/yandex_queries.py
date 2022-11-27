from datetime import date
import requests

URL_DIRECT_ADS = "https://api.direct.yandex.com/json/v5/ads"
URL_DIRECT_REPORTS = "https://api.direct.yandex.com/json/v5/reports"
URL_DIRECT_CLIENTS = "https://api.direct.yandex.com/json/v5/clients"
CLIENT_ID = "6e6aa9ec2f79451cb3e773a5f80f7ef0"
CLIENT_SECRET = "0edf762fd750444190568a434004ffbe"
URL_OAUTH = f"https://oauth.yandex.ru/authorize?response_type=code&client_id={CLIENT_ID}"
VERIFY_URL = "https://oauth.yandex.ru/token"


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


async def verify_direct(code: str) -> str:
    """Verify code to get token"""
    data = {"grant_type": "authorization_code", "code": code, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
    access_token = requests.post(VERIFY_URL, data=data).json()
    if access_token.get("access_token") is not None:
        return access_token.get("access_token")


async def get_login_direct(token: str):
    direct_headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Language": "en",
        "skipReportHeader": "true",
        "skipReportSummary": "true",
        "returnMoneyInMicros": "false",
    }
    direct_params = {
        "method": "get",
        "params": {
            "FieldNames": ["Login"],
        },
    }
    response_report = requests.post(url=URL_DIRECT_CLIENTS, json=direct_params, headers=direct_headers).json()
    return response_report["result"]["Clients"][0]["Login"]
