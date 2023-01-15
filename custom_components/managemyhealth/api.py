"""ManageMyHealth API"""
import logging
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
import json

_LOGGER = logging.getLogger(__name__)

class MmhAPI:
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._api_token = ''
        self._user_id = ''
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
                self.get_appointments()
                result = True
            else:
                _LOGGER.error("Error occured logging in 2")
        else:
            _LOGGER.error("Error occured logging in 1")
            #_LOGGER.error(loginResult.text)
        return result

    def get_profile(self):
        """Get profile."""
        result = False
        data = {
            "requestPage": "",
            "RequestParams": [{
                "key": "userid",
                "value": ""
            }]
        }
        headers = {
            "Authorization": "Bearer " + self._api_token
        }
        loginResult = requests.post(self._url_base + "/api/UserProfile/GetUserProfileByUserId", json=data, headers=headers)
        if loginResult.UserId:
            jsonResult = loginResult.json()
            self._user_id = jsonResult['UserId']
            _LOGGER.debug('Successfully logged in')
            self.get_appointments()
            result = True
        else:
            _LOGGER.error(loginResult.text)
        return result

    def check_auth(self):
        """Check to see if our UserID is valid."""
        if self._user_id:
            _LOGGER.debug('Login is valid')
            return True
        else:
            if self.login() == False:
                _LOGGER.debug(result.text)
                return False
            return True

    def get_appointments(self):
        data = {
            "requestPage": "",
            "RequestParams": [{
                "key": "userid",
                "value": ""
            }]
        }
        headers = {
            "Authorization": "Bearer " + self._api_token
        }
        response = requests.post(self._url_base + "/api/Appointments/GetPatientAppointments", json=data, headers=headers)
        data = {}
        if response.status_code == requests.codes.ok:
            data = response.json()
            if not data:
                _LOGGER.warning('Fetched appointments successfully, but did not find any')
            return data
        else:
            _LOGGER.error('Failed to fetch appointments')
            return data
