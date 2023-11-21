"""ManageMyHealth sensors"""
from datetime import datetime, timedelta

import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .api import MMHApi

from .const import DOMAIN, SENSOR_NAME_APPOINTMENT, SENSOR_NAME_MESSAGES_PERSONAL

NAME = DOMAIN
ISSUEURL = "https://github.com/codyc1515/hacs_managemyhealth/issues"

STARTUP = f"""
-------------------------------------------------------------------
{NAME}
This is a custom component
If you have any issues with this you need to open an issue here:
{ISSUEURL}
-------------------------------------------------------------------
"""

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_EMAIL): cv.string, vol.Required(CONF_PASSWORD): cv.string}
)

SCAN_INTERVAL = timedelta(minutes=60)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,
):
    email = entry.data.get(CONF_EMAIL)
    password = entry.data.get(CONF_PASSWORD)

    api = MMHApi(email, password)

    _LOGGER.debug("Setting up sensor(s)...")

    sensors = []
    sensors.append(MMHAppointmentsSensor(SENSOR_NAME_APPOINTMENT, api))
    #sensors.append(MMHPersonalMessagesSensor(SENSOR_NAME_MESSAGES_PERSONAL, api))
    async_add_entities(sensors, True)


class MMHAppointmentsSensor(Entity):
    def __init__(self, name, api):
        self._name = name
        self._icon = "mdi:doctor"
        self._state = ""
        self._state_attributes = {}
        self._unit_of_measurement = None
        self._unique_id = f"{DOMAIN}_appointments"
        self._device_class = "timestamp"
        self._api = api

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._state_attributes

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def device_class(self):
        """Return the device class."""
        return self._device_class

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    def update(self):
        _LOGGER.debug("Fetching appointments")
        data = []
        response = self._api.get_appointments()
        if response:
            _LOGGER.debug(response)
            for appointment in response:
                app_from_time_slot = appointment.get("AppFromTimeSlot")
                if app_from_time_slot is None:
                    self._state = None
                    break

                date_object = datetime.strptime(
                    app_from_time_slot + "+1300", "%Y-%m-%dT%H:%M:%S%z"
                )
                self._state = date_object.isoformat()

                self._state_attributes["Duration"] = (
                    str(appointment["Duration"]) + " mins"
                )
                self._state_attributes["Reason"] = appointment["reasontovisit"]

                self._state_attributes["Location Name"] = appointment["BusinessName"]
                self._state_attributes["Provider Name"] = appointment["Providername"]

                _LOGGER.debug("AppFromTimeSlot | " + app_from_time_slot)
                _LOGGER.debug("isoformat | " + date_object.isoformat())

                # Because we are ordering by date in the API call, to get the soonest appointment we only ever need the first result
                break

        else:
            self._state = None
            _LOGGER.debug("Found no appointments on refresh")


class MMHPersonalMessagesSensor(Entity):
    def __init__(self, name, api):
        self._name = name
        self._icon = "mdi:doctor"
        self._state = ""
        self._state_attributes = {}
        self._unit_of_measurement = None
        self._unique_id = f"{DOMAIN}_messages"
        self._device_class = "timestamp"
        self._api = api

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._state_attributes

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def device_class(self):
        """Return the device class."""
        return self._device_class

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    def update(self):
        _LOGGER.debug("Fetching personal messages")
        data = []
        response = self._api.get_personal_messages()
        if response:
            _LOGGER.debug(response)
            for message in response:
                self._state = message.Subject

                date_object = datetime.strptime(
                    message["InsertTimeStamp"] + "+1300", "%Y-%m-%dT%H:%M:%S%z"
                )
                self._state = date_object.isoformat()

                self._state_attributes["Message"] = message["MessageBody"]
                self._state_attributes["From"] = appointment["FromName"]

                # Because we are ordering by date in the API call, to get the soonest appointment we only ever need the first result
                break
        else:
            self._state = None
            _LOGGER.debug("Found no personal messages on refresh")