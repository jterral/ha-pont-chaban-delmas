"""Config flow for Pont Chaban-Delmas integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, LOGGER
from .pont_chaban import PontChabanRepository


async def validate_connection(hass: HomeAssistant) -> dict[str, Any]:
    """Validate that we can connect to the Pont Chaban API.

    Parameters:
        hass: Home Assistant instance.

    Returns:
        dict: Information about the connection.

    Raises:
        CannotConnect: If unable to connect to the API.
        InvalidData: If the API returns invalid data.
    """
    repository = PontChabanRepository()
    try:
        # Try to fetch data to validate the connection
        closures = await repository.get_upcoming_closures(limit=1)
        if not closures:
            raise InvalidData("No data returned from API")

        return {"title": "Pont Chaban-Delmas"}
    except Exception as err:
        LOGGER.error("Error connecting to Pont Chaban API: %s", err)
        raise CannotConnect from err
    finally:
        await repository.close()


class PontChabanConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pont Chaban-Delmas."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_connection(self.hass)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidData:
                errors["base"] = "invalid_data"
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create the config entry
                return self.async_create_entry(title=info["title"], data={})

        # Show the configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidData(HomeAssistantError):
    """Error to indicate we got invalid data."""
