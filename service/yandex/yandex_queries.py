import asyncio
from datetime import datetime

import requests
import time
from loguru import logger

import cfg

URL_DIRECT_ADS = "https://api.direct.yandex.com/json/v5/ads"
URL_DIRECT_REPORTS = "https://api.direct.yandex.com/json/v5/reports"
URL_DIRECT_CLIENTS = "https://api.direct.yandex.com/json/v5/clients"
GOALS_URL = "https://api.direct.yandex.ru/live/v4/json/"
URL_AGENCY_CLIENTS = "https://api.direct.yandex.com/json/v5/agencyclients"
# URL_DIRECT_ADS = "https://api-sandbox.direct.yandex.com/json/v5/ads"
# URL_DIRECT_REPORTS = "https://api-sandbox.direct.yandex.com/json/v5/reports"
# URL_DIRECT_CLIENTS = "https://api-sandbox.direct.yandex.com/json/v5/clients"

CLIENT_ID = cfg.config.yandex.yandex_client_id
CLIENT_SECRET = cfg.config.yandex.yandex_client_secret
URL_OAUTH = f"https://oauth.yandex.ru/authorize?response_type=code&client_id={CLIENT_ID}"
VERIFY_URL = "https://oauth.yandex.ru/token"

# GOALS_URL = "https://api-sandbox.direct.yandex.com/live/v4/json"
# URL_AGENCY_CLIENTS = "https://api-sandbox.direct.yandex.com/json/v5/agencyclients"


def get_daily_data_request(
        token: str,
        goals: int,
        login: str,
        account_id: int,
        date_start: str,
        date_end: str) -> requests.Response:
    """Request to Yandex.Direct API to get daily data"""
    direct_headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Language": "en",
        "skipReportHeader": "true",
        "Client-Login": login,
        "skipReportSummary": "true",
        "returnMoneyInMicros": "false",
    }

    direct_params = {
        "params": {
            "SelectionCriteria": {},
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
            "ReportName": f"Report_{account_id}__00",
            "ReportType": "CUSTOM_REPORT",
            "DateRangeType": "AUTO",
            "Format": "TSV",
            "IncludeVAT": "NO",
        }
    }

    if date_start is not None and date_end is not None:
        direct_params['params']['DateRangeType'] = 'CUSTOM_DATE'
        direct_params['params']['SelectionCriteria'] = {'DateFrom': date_start, 'DateTo': date_end}


    if goals is not None:
        direct_params['params']['Goals'] = [goals]
        direct_params['params']['AttributionModels'] = ['LSC']

    response_report = requests.get(url=URL_DIRECT_REPORTS, headers=direct_headers, json=direct_params)
    return response_report


def get_daily_data_request_tg(token: str, goals: int, login: str) -> requests.Response:
    """Request to Yandex.Direct API to get daily data for telegram bot"""
    direct_headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Language": "ru",
        "skipReportHeader": "true",
        "skipReportSummary": "true",
        "Client-Login": login,
        "returnMoneyInMicros": "false",
    }

    field_names = [
        "Date",
        "CampaignName",
        "Criterion",
        "Impressions",
        "Clicks",
        "Cost",
    ]

    if goals is not None:
        field_names.append("Conversions")

    direct_params = {
        "params": {
            "SelectionCriteria": {},
            "FieldNames": field_names,
            "ReportName": f"Report_telegram_{datetime.today()}",
            "ReportType": "CUSTOM_REPORT",
            "DateRangeType": "YESTERDAY",
            "Format": "TSV",
            "IncludeVAT": "NO",
        }
    }

    if goals is not None:
        direct_params["params"]["Goals"] = [goals]
        direct_params["params"]["AttributionModels"] = ["LSC"]

    response_report = requests.get(url=URL_DIRECT_REPORTS, headers=direct_headers, json=direct_params)

    if response_report.status_code == 201 or response_report.status_code == 202:
        while not response_report.status_code == 200:
            time.sleep(20)
            response_report = requests.get(url=URL_DIRECT_REPORTS, headers=direct_headers, json=direct_params)
    return response_report


async def verify_direct(code: str) -> str:
    """Verify code to get token"""
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    access_token = requests.post(VERIFY_URL, data=data).json()
    if access_token.get("access_token") is not None:
        return access_token.get("access_token")


async def get_login_direct(token: str) -> tuple[str, str]:
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
            "FieldNames": ["Login", "Type"],
        },
    }
    response_report = requests.post(url=URL_DIRECT_CLIENTS, json=direct_params, headers=direct_headers)
    try:
        login = response_report.json()["result"]["Clients"][0]["Login"]
        account_type = response_report.json()["result"]["Clients"][0]["Type"]
        return login, account_type
    except KeyError:
        logger.error(f"Error getting login. {response_report.text}")
        return "Error", ""


async def get_agency_logins(token: str) -> list:
    headers = {"Authorization": f"Bearer {token}"}

    params = {
        "method": "get",
        "params": {
            "SelectionCriteria": {
                "Archived": "NO",
            },
            "FieldNames": ["Login"],
        },
    }
    response = requests.post(url=URL_AGENCY_CLIENTS, json=params, headers=headers)
    logins = [login["Login"] for login in response.json()["result"]["Clients"]]
    return logins


async def get_arr_goals(token: str, campaign: str, login: str) -> requests.Response:
    """Query to get list of goals"""
    direct_params = {
        "method": "GetStatGoals",
        "token": token,
        "Client-Login": login,
        "param": {"CampaignID": campaign},
    }
    response_report = requests.post(GOALS_URL, json=direct_params)
    return response_report


async def query_get_arr_campaigns(token: str, login: str) -> requests.Response:
    """Query to get list of campaigns"""
    direct_headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Language": "en",
        "Client-Login": login,
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
    if resp.status_code == 201 or resp.status_code == 202:
        while not resp.status_code == 200:
            await asyncio.sleep(1)
            resp = requests.post(URL_DIRECT_REPORTS, json=direct_params, headers=direct_headers)
    return resp
