"""Constants for the ManageMyHealth sensors"""
from homeassistant.const import Platform

DOMAIN = 'managemyhealth'
SENSOR_NAME = "ManageMyHealth"

SENSOR_NAME_APPOINTMENT = 'Appointment'
SENSOR_NAME_MAILBOX = 'Message'

PLATFORMS = [
    Platform.SENSOR,
]