"""Adds config flow for ManageMyHealth."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    MmhApi,
    MmhApiAuthenticationError,
    MmhApiCommunicationError,
    MmhApiError,
)
from .const import DOMAIN, LOGGER


class MmhFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for ManageMyHealth."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self.async_set_unique_id(user_input[CONF_EMAIL])
                self._abort_if_unique_id_configured()
                # TODO: check if unique id from account is in use (NHI?)

                await self._test_credentials(
                    email=user_input[CONF_EMAIL],
                    password=user_input[CONF_PASSWORD],
                )
            except MmhApiAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "invalid_auth"
            except MmhApiCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "cannot_connect"
            except MmhApiError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_EMAIL],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_EMAIL,
                        default=(user_input or {}).get(CONF_EMAIL),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.EMAIL,
                            autocomplete="email"
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                            autocomplete="password"
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    async def _test_credentials(self, email: str, password: str) -> None:
        """Validate credentials."""
        api = MmhApi(
            email=email,
            password=password,
            session=async_create_clientsession(self.hass),
        )
        await api.login()
