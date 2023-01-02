from datetime import date
import requests

URL_DIRECT_ADS = "https://api.direct.yandex.com/json/v5/ads"
URL_DIRECT_REPORTS = "https://api.direct.yandex.com/json/v5/reports"
URL_DIRECT_CLIENTS = "https://api.direct.yandex.com/json/v5/clients"
CLIENT_ID = "6e6aa9ec2f79451cb3e773a5f80f7ef0"
CLIENT_SECRET = "0edf762fd750444190568a434004ffbe"
URL_OAUTH = f"https://oauth.yandex.ru/authorize?response_type=code&client_id={CLIENT_ID}"
VERIFY_URL = "https://oauth.yandex.ru/token"
GOALS_URL = "https://api.direct.yandex.ru/live/v4/json/"


def get_daily_data_request(token: str, dashboard_id: int, goals: int) -> requests.Response:
    """Request to Yandex.Direct API to get daily data"""
    direct_headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Language": "en",
        "skipReportHeader": "true",
        "skipReportSummary": "true",
        "returnMoneyInMicros": "false",
    }

    direct_params = {
        "params": {
            "SelectionCriteria": {},
            "Goals": [goals],
            "AttributionModels": ["LSC"],
            "FieldNames": [
                "Date",
                "CampaignId",
                "CampaignName",
                "CampaignType",
                "AdGroupId",
                "AdGroupName",
                "Age",
                "TargetingLocationId",
                "TargetingLocationName",
                "Gender",
                "Criterion",
                "CriterionId",
                "CriterionType",
                "Device",
                "Impressions",
                "Clicks",
                "Cost",
                "Bounces",
                "Conversions",
            ],
            "ReportName": f"Report_{date.today()}_{dashboard_id}",
            "ReportType": "CUSTOM_REPORT",
            "DateRangeType": "AUTO",
            "Format": "TSV",
            "IncludeVAT": "NO",
        }
    }

    response_report = requests.get(url=URL_DIRECT_REPORTS, headers=direct_headers, json=direct_params)
    return response_report


def get_daily_data_request_tg(token: str, dashboard_id: int, goals: int) -> requests.Response:
    """Request to Yandex.Direct API to get daily data for telegram bot"""
    direct_headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Language": "en",
        "skipReportHeader": "true",
        "skipReportSummary": "true",
        "returnMoneyInMicros": "false",
    }

    direct_params = {
        "params": {
            "SelectionCriteria": {},
            "Goals": [goals],
            "AttributionModels": ["LSC"],
            "FieldNames": [
                "Date",
                "CampaignName",
                "Criterion",
                "Impressions",
                "Clicks",
                "Cost",
                "Conversions",
            ],
            "ReportName": f"Report_for_tg_{date.today()}_{dashboard_id}",
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


async def get_login_direct(token: str) -> str:
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


async def get_arr_goals(token: str, campaign: str) -> requests.Response:
    """Query to get list of goals"""
    direct_params = {"method": "GetStatGoals", "token": token, "param": {"CampaignID": campaign}}
    response_report = requests.post(GOALS_URL, json=direct_params)
    return response_report


async def get_arr_campaigns(token: str) -> requests.Response:
    """Query to get list of campaigns"""
    direct_headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Language": "en",
        "skipReportHeader": "true",
        "skipReportSummary": "true",
    }
    direct_params = {
        "params": {
            "SelectionCriteria": {},
            "FieldNames": [
                "CampaignId",
            ],
            "ReportName": "Get_CampaignsID_date",
            "ReportType": "CUSTOM_REPORT",
            "DateRangeType": "LAST_30_DAYS",
            "Format": "TSV",
            "IncludeVAT": "NO",
        }
    }

    resp = requests.post(URL_DIRECT_REPORTS, json=direct_params, headers=direct_headers)
    return resp
