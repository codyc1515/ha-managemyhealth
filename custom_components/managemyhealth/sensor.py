"""Sensor platform for ManageMyHealth."""

from __future__ import annotations
import logging

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .const import DOMAIN
from .coordinator import MmhDataUpdateCoordinator
from .entity import MmhEntity

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="sensor",
        name="Health Appointment",
        icon="mdi:doctor",
    ),
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        MmhSensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class MmhSensor(MmhEntity, SensorEntity):
    """ManageMyHealth Sensor class."""

    def __init__(
        self,
        coordinator: MmhDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        if self.coordinator.data["appointment"]:
            _LOGGER.debug("Found sensor data")
            return self.coordinator.data["appointment"]["start"]
        else:
            _LOGGER.debug("Couldn't find sensor data")
            return None
