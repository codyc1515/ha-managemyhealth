"""ManageMyHealth API"""
import logging
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
import json

_LOGGER = logging.getLogger(__name__)

class MMHApi:
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._api_token = None
        self._user_id = None
        self._url_base = 'https://wapiv2.managemyhealth.co.nz'

    def login(self):
        """Login to the API."""
        result = False
        data = {
            "grant_type": "password",
            "username": self._username,
            "password": self._password
        }
        loginResult = requests.post(self._url_base + "/authaccess_token", data=data)
        if loginResult.status_code == requests.codes.ok:
            jsonResult = loginResult.json()
            if jsonResult['token_type'] == "bearer":
                self._api_token = jsonResult['access_token']
                _LOGGER.debug('Successfully logged in')
                result = True
            else:
                _LOGGER.error("Error occured logging in 2")
        else:
            _LOGGER.error("Error occured logging in 1")
        return result

    def get_appointments(self):
        if not self._api_token:
            self.login()
        
        data = {
            "requestPage": "",
            "RequestParams": [{
                "key": "userid",
                "value": ""
            }]
        }
        headers = {
            "Accept: application/json",
            "Authorization": "Bearer " + self._api_token
        }
        response = requests.post(self._url_base + "/api/Appointments/GetPatientAppointments", json=data, headers=headers)
        data = {}
        if response.status_code == requests.codes.ok:
            data = response.json()
            if not data:
                _LOGGER.debug('Fetched appointments successfully, but did not find any')
            return data
        else:
            _LOGGER.error('Failed to fetch appointments')
            return data

    def get_personal_messages(self):
        if not self._api_token:
            self.login()
        
        headers = {
            "Accept: application/json",
            "Authorization": "Bearer " + self._api_token
        }
        response = requests.post(self._url_base + "/api/Inbox/GetReceivedMessages", headers=headers)
        data = {}
        if response.status_code == requests.codes.ok:
            data = response.json()
            if not data:
                _LOGGER.debug('Fetched personal messages successfully, but did not find any')
            return data
        else:
            _LOGGER.error('Failed to fetch personal messages')
            return data