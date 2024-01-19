"""ManageMyHealth API."""
from __future__ import annotations
import logging

import asyncio
import socket

import aiohttp
import async_timeout

from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)


class MmhApiError(Exception):
    """Exception to indicate a general API error."""


class MmhApiCommunicationError(
    MmhApiError
):
    """Exception to indicate a communication error."""


class MmhApiAuthenticationError(
    MmhApiError
):
    """Exception to indicate an authentication error."""


class MmhApi:
    """ManageMyHealth API."""

    def __init__(
        self,
        email: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """ManageMyHealth API."""
        self._email = email
        self._password = password
        self._session = session
        self._token = None
        self._server = 'https://mapiv3.managemyhealth.co.nz'

    async def login(self) -> any:
        """Login to the API."""
        response = await self._api_wrapper(
            method="post",
            url=self._server + "/authaccess_token",
            data={
                "grant_type": "password",
                "username": self._email,
                "password": self._password
            }
        )

        if response.get('token_type') == "bearer":
            self._token = response.get('access_token')
            return True
        else:
            raise MmhApiAuthenticationError(
                "Invalid credentials but was this part required?",
            )
            return False

    async def get_appointments(self) -> any:
        """Get data from the API."""
        if not self._token:
            await self.login()

        # Get appointments
        _LOGGER.debug('Fetching current appointments')
        appointments = await self._api_wrapper(
            method="post",
            url=self._server + "/api/Appointments/GetPatientAppointments",
            json={
                "requestPage": "",
                "RequestParams": [{
                    "key": "userid",
                    "value": ""
                }]
            },
            headers={"Authorization": "Bearer " + self._token},
        )

        if appointments:
            _LOGGER.debug('Fetched current appointments')
            
            # Loop through the appointment(s)
            for appointment in appointments:
                # Skip cancelled or rejected
                if appointment['appstatus'] == 'Cancelled' or appointment['IsApproved'] == 'Rejected':
                    continue

                # If there was no appointment time, skip it
                if appointment.get("AppFromTimeSlot") is None:
                    continue

                _LOGGER.debug('Found future appointment')

                # Get the appointment time
                start = datetime.strptime(appointment.get("AppFromTimeSlot") + "+1300", "%Y-%m-%dT%H:%M:%S%z")

                # Calculate the end time from the duration
                end = start + timedelta(minutes=appointment.get("Duration"))

                # Find the providers name
                summary = appointment.get("Providername")

                # Find the reason to visit
                description = appointment.get("reasontovisit")

                # Find the location
                location = appointment.get("BusinessName")

                # Because we are ordering by date in the API call, to get the soonest appointment we only ever need the first result
                return {
                    "appointment": {
                        "start": start,
                        "end": end,
                        "summary": summary,
                        "description": description,
                        "location": location,
                        "raw": appointment
                    }
                }

            _LOGGER.debug('Found no future appointments, looking for past appointments')
            return await self.get_appointments_past()
        else:
            _LOGGER.debug('Found no future appointments, looking for past appointments')
            return await self.get_appointments_past()

    async def get_appointments_past(self) -> any:
        """Get data from the API."""
        if not self._token:
            await self.login()

        # Get appointments
        _LOGGER.debug('Fetching past appointments')
        appointments = await self._api_wrapper(
            method="post",
            url=self._server + "/api/Appointments/GetPastAppointmentsPaging",
            json={
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
            },
            headers={"Authorization": "Bearer " + self._token},
        )

        if appointments:
            _LOGGER.debug('Fetched past appointments')
            
            # Loop through the appointment(s)
            for appointment in appointments:
                # If there was no appointment time, skip it
                if appointment.get("AppFromTimeSlot") is None:
                    return False
                    break

                _LOGGER.debug('Found past appointment')
                
                # Get the appointment time
                start = datetime.strptime(appointment.get("AppFromTimeSlot") + "+1300", "%Y-%m-%dT%H:%M:%S%z")

                # Calculate the end time from the duration (past appointments don't have a Duration, so guess it was 15)
                end = start + timedelta(minutes=15)

                # Find the providers name
                summary = appointment.get("Providername")

                # Find the reason to visit
                description = appointment.get("reasontovisit")

                # Find the location
                location = appointment.get("BusinessName")

                # Because we are ordering by date in the API call, to get the soonest appointment we only ever need the first result
                return {
                    "appointment": {
                        "start": start,
                        "end": end,
                        "summary": summary,
                        "description": description,
                        "location": location,
                        "raw": appointment
                    }
                }

            _LOGGER.warning('Could not find any appointments')
            return False
        else:
            raise MmhApiError(
                "Something really wrong happened",
            )
            return False

    async def async_set_data(self, value: str) -> any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"title": value},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        json: dict | None = None,
        headers: dict | None = None,
    ) -> any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    data=data,
                    json=json,
                    headers=headers,
                )
                if response.status in (401, 403):
                    raise MmhApiAuthenticationError(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()

        except asyncio.TimeoutError as exception:
            raise MmhApiCommunicationError(
                "Timeout error fetching information: %s", exception
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise MmhApiCommunicationError(
                "Error fetching information: %s", exception
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise MmhApiError(
                "Something really wrong happened!: %s", exception
            ) from exception
