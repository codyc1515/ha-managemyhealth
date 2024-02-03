"""DataUpdateCoordinator for ManageMyHealth."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import (
    MmhApi,
    MmhApiAuthenticationError,
    MmhApiError,
)
from .const import DOMAIN, LOGGER


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class MmhDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        api: MmhApi,
    ) -> None:
        """Initialize."""
        self.api = api
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=30),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.api.get_appointments()
        except MmhApiAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except MmhApiError as exception:
            raise UpdateFailed(exception) from exception
