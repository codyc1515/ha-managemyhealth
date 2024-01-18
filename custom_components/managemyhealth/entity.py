"""ManageMyHealth Entity class."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, NAME, VERSION
from .coordinator import MmhDataUpdateCoordinator


class MmhEntity(CoordinatorEntity):
    """ManageMyHealth Entity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: MmhDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            configuration_url="https://app.managemyhealth.co.nz/dashboards/dashboard",
            entry_type=DeviceEntryType.SERVICE,
            manufacturer=NAME,
            model=VERSION,
            name=NAME,
            suggested_area="Health"
        )
