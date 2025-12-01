import asyncio
from dataclasses import dataclass
from types import TracebackType
from typing import List, Optional, Type
import aiohttp

@dataclass(frozen=True)
class BridgeResponse:
    bateau: str
    date_passage: str
    fermeture_a_la_circulation: str
    re_ouverture_a_la_circulation: str
    type_de_fermeture: str
    fermeture_totale: str

@dataclass(frozen=True)
class ApiResponse:
    total_count: int
    results: List[BridgeResponse]

    @classmethod
    def from_json(cls, data: dict) -> "ApiResponse":
        results = [
            BridgeResponse(**item)
            for item in data["results"]
        ]
        return cls(
            total_count=data["total_count"],
            results=results,
        )

class PontChaban:
    """Class representing the Pont Chaban bridge."""

    BASE_ADDRESS = "https://datahub.bordeaux-metropole.fr"

    def __init__(self):
        """Initialize the Pont Chaban bridge component."""
        self._base_address = self.BASE_ADDRESS
        self._client = aiohttp.ClientSession(raise_for_status=True)

    async def close(self) -> None:
        return await self._client.close()

    async def __aenter__(self) -> "PontChaban":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None

    def _make_url(self):
        return self._base_address + "/api/explore/v2.1/catalog/datasets/previsions_pont_chaban/records"

    async def fetch_data(self) -> ApiResponse:
        """Fetch data related to the Pont Chaban bridge."""
        async with self._client.get(self._make_url()) as resp:
            ret = await resp.json()
            return ApiResponse.from_json(ret)
