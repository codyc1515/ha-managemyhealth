import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta
import json

_LOGGER = logging.getLogger(__name__)

class MMHApi:
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._api_token = None
        self._user_id = None
        self._url_base = 'https://mapiv3.managemyhealth.co.nz'

    async def login(self):
        """Login to the API."""
        result = False
        data = {
            "grant_type": "password",
            "username": self._username,
            "password": self._password
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self._url_base + "/authaccess_token", data=data) as response:
                if response.status == 200:
                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        json_result = await response.json()
                        if json_result.get('token_type') == "bearer":
                            _LOGGER.debug('Successfully logged in')
                            self._api_token = json_result['access_token']
                            result = True
                        else:
                            _LOGGER.error("Error occurred logging in 2")
                    else:
                        _LOGGER.error(f"Unexpected content type: {content_type}, Response content: {await response.text()}")
                else:
                    _LOGGER.error(f"Error occurred logging in 1. Response content: {await response.text()}")
        return result

    async def get_appointments(self):
        if not self._api_token:
            await self.login()

        data = {
            "requestPage": "",
            "RequestParams": [{
                "key": "userid",
                "value": ""
            }]
        }
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + self._api_token
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self._url_base + "/api/Appointments/GetPatientAppointments", json=data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data:
                        _LOGGER.debug('Fetched appointments successfully, but did not find any; looking for past appointments')
                        return await self.get_past_appointments()
                    else:
                        return data
                else:
                    _LOGGER.error('Failed to fetch appointments')
                    return {}

    async def get_past_appointments(self):
        if not self._api_token:
            await self.login()

        data = {
            "requestPage": "",
            "RequestParams": [{
                "key": "UserId",
                "value": ""
            }, {
                "key": "strindx",
                "value": 0
            }, {
                "key": "EndIndx",
                "value": 20
            }]
        }
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + self._api_token
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self._url_base + "/api/Appointments/GetPastAppointmentsPaging", json=data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data:
                        _LOGGER.debug('Fetched past appointments successfully, but did not find any')
                    return data
                else:
                    _LOGGER.error('Failed to fetch past appointments')
                    return {}

    async def get_mailbox(self):
        if not self._api_token:
            await self.login()

        data = {
            "requestPage": "",
            "RequestParams": [{
                "key": "UserId",
                "value": ""
            }, {
                "key": "startIndx",
                "value": 0
            }, {
                "key": "EndIndx",
                "value": 20
            }]
        }
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + self._api_token
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self._url_base + "/api/Inbox/GetReceivedMessages", json=data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data:
                        _LOGGER.debug('Fetched personal messages successfully, but did not find any')
                    return data
                else:
                    _LOGGER.error('Failed to fetch personal messages')
                    return {}
