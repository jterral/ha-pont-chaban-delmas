""""Data update coordinator for pont-chaban-delmas integration."""
from __future__ import annotations

from datetime import timedelta
from typing import List
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .application import BridgeScheduleService
from .infrastructure import OdataClient
from .domain import BridgeClosure

class PontChabanCoordinator(DataUpdateCoordinator[List[BridgeClosure]]):
    def __init__(self, hass: HomeAssistant, hours: int, limit: int = 50):
        super().__init__(hass, hass.logger, name="Pont Chaban-Delmas", update_interval=timedelta(hours=hours))
        self._service = BridgeScheduleService(OdataClient())
        self._limit = limit

    async def _async_update_data(self) -> List[BridgeClosure]:
        try:
            return await self._service.get_upcoming(limit=self._limit)
        except Exception as err:
            raise UpdateFailed(err) from err
