"""Application service to get bridge closure schedules."""

from __future__ import annotations

from typing import List
from homeassistant.util import dt as dt_util
from .infrastructure import OdataClient, dto_to_domain
from .domain import BridgeClosure

class BridgeScheduleService:
    def __init__(self, client: OdataClient):
        self._client = client

    async def get_upcoming(self, limit: int = 50) -> List[BridgeClosure]:
        dtos = await self._client.fetch_closures(limit=limit)
        closures = [dto_to_domain(d) for d in dtos]
        now = dt_util.utcnow()
        closures = [c for c in closures if c.is_future(now)]
        closures.sort(key=lambda c: c.start_utc)
        return closures
