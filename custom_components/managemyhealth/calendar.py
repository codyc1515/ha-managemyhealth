"""Calendar platform for ManageMyHealth."""
from __future__ import annotations

import logging
import datetime

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription

from .const import DOMAIN
from .coordinator import MmhDataUpdateCoordinator
from .entity import MmhEntity


ENTITY_DESCRIPTIONS = (
    EntityDescription(
        key="calendar",
        name="Health Appointment",
        icon="mdi:doctor",
    ),
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the calendar platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        MmhCalendar(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class MmhCalendar(MmhEntity, CalendarEntity):
    """ManageMyHealth Calendar class."""

    def __init__(
        self,
        coordinator: MmhDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the calendar class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._event: CalendarEvent | None = None

    @property
    def event(self) -> CalendarEvent:
        """Return the next upcoming event."""
        if self.coordinator.data and self.coordinator.data['appointment']:
            _LOGGER.debug('Found event')
            self._event = CalendarEvent(
                start=self.coordinator.data['appointment']['start'],
                end=self.coordinator.data['appointment']['end'],
                summary=self.coordinator.data['appointment']['summary'],
                description=self.coordinator.data['appointment']['description'],
                location=self.coordinator.data['appointment']['location'],
            )
        else:
            _LOGGER.debug('No events found')
            self._event = None
        return self._event

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        ''' # not sure this is required
        assert start_date < end_date
        if self._event.start_datetime_local >= end_date:
            return []
        if self._event.end_datetime_local < start_date:
            return []
        '''
        return [self._event]
