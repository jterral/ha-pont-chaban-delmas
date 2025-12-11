"""DataUpdateCoordinator for Pont Chaban-Delmas integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DOMAIN, LOGGER
from .domain import BridgeClosure
from .pont_chaban import PontChabanRepository


class PontChabanCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage data updates from Pont Chaban API.

    Orchestrates data fetching from the repository and transforms it for
    presentation layer consumption. Acts as the application/use-cases layer
    in the DDD architecture.
    """

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator.

        Parameters:
            hass: Home Assistant instance.
        """
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=15),  # Update every 15 minutes
        )
        self.repository = PontChabanRepository()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from repository and prepare for sensors.

        Returns:
            dict: Processed closure data with upcoming closures and next closure.

        Raises:
            UpdateFailed: If unable to fetch or process data.
        """
        try:
            LOGGER.debug("Fetching Pont Chaban closures from repository")

            # Get domain objects directly from repository
            closures: list[BridgeClosure] = await self.repository.get_upcoming_closures(
                limit=20
            )
            now = dt_util.utcnow()

            # Filter to only future closures (in case repository returns historical)
            upcoming = [c for c in closures if c.is_upcoming(now)]

            LOGGER.info("Successfully processed %d upcoming closures", len(upcoming))

            # Extract next closure
            next_closure = upcoming[0] if upcoming else None

            return {
                "closures": upcoming,
                "next_closure": next_closure,
                "last_update": now,
            }

        except Exception as err:
            LOGGER.error("Error fetching Pont Chaban data: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def async_shutdown(self) -> None:
        """Clean up resources when shutting down."""
        LOGGER.debug("Shutting down Pont Chaban coordinator")
        await self.repository.close()
