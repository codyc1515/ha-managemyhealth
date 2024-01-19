"""Calendar platform for ManageMyHealth."""
from __future__ import annotations
import logging

from homeassistant.components.calendar import CalendarEntity, CalendarEvent

from .const import DOMAIN
from .coordinator import MmhDataUpdateCoordinator
from .entity import MmhEntity

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="calendar",
        name="Health Appointments",
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
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the calendar class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._event: CalendarEvent | None = None

    @property
    def event(self) -> CalendarEvent:
        """Return the next upcoming event."""
        _LOGGER.debug(self.coordinator)
        _LOGGER.debug(self.coordinator.data)
        if self.coordinator.data['appointment']:
            # self.coordinator.data['appointment']['date']
            half_hour_from_now = dt_util.now() + datetime.timedelta(minutes=0)
            self._event = CalendarEvent(
                start=half_hour_from_now,
                end=half_hour_from_now + datetime.timedelta(minutes=15),
                summary="Future Event",
                description="Future Description",
                location="Future Location",
            )
        else:
            return None 
        return self._event

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        assert start_date < end_date
        if self._event.start_datetime_local >= end_date:
            return []
        if self._event.end_datetime_local < start_date:
            return []
        return [self._event]
