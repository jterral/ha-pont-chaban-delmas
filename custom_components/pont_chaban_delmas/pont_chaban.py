from dataclasses import dataclass
from types import TracebackType
from typing import List, Optional, Type
import aiohttp

from .const import LOGGER

@dataclass(frozen=True)
class BridgeResponse:
    """Response data for a single bridge passage event.

    Attributes:
        bateau: Name of the boat passing through.
        date_passage: Date and time of the passage.
        fermeture_a_la_circulation: Road closure time.
        re_ouverture_a_la_circulation: Road reopening time.
        type_de_fermeture: Type of closure.
        fermeture_totale: Whether it's a total closure.
    """
    bateau: str
    date_passage: str
    fermeture_a_la_circulation: str
    re_ouverture_a_la_circulation: str
    type_de_fermeture: str
    fermeture_totale: str

    @classmethod
    def from_json(cls, data: dict) -> "BridgeResponse":
        """Create a BridgeResponse from JSON data.

        Parameters:
            data: Dictionary containing bridge response fields.

        Returns:
            BridgeResponse: Instance created from JSON data.
        """
        return cls(**data)

@dataclass(frozen=True)
class ApiResponse:
    """API response containing bridge passage records.

    Attributes:
        total_count: Total number of records available.
        results: List of bridge passage events.
    """
    total_count: int
    results: List[BridgeResponse]

    @classmethod
    def from_json(cls, data: dict) -> "ApiResponse":
        """Create an ApiResponse from JSON data.

        Parameters:
            data: Dictionary containing API response with 'total_count' and 'results'.

        Returns:
            ApiResponse: Instance with parsed bridge responses.
        """
        results = [
            BridgeResponse.from_json(item) for item in data["results"]
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
        LOGGER.debug("Initializing PontChaban client")
        self._base_address = self.BASE_ADDRESS
        self._client = aiohttp.ClientSession(raise_for_status=True)

    async def close(self) -> None:
        LOGGER.debug("Closing PontChaban client")
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

    def _make_url(self) -> str:
        return self._base_address + "/api/explore/v2.1/catalog/datasets/previsions_pont_chaban/records"

    async def fetch_data(self, limit: int = 10) -> ApiResponse:
        """Fetch data related to the Pont Chaban bridge.

        Parameters:
            limit: Maximum number of records to fetch (default: 10).

        Returns:
            ApiResponse: Parsed API response with bridge passage events.

        Raises:
            aiohttp.ClientError: If the HTTP request fails.
            ValueError: If the response data is invalid.
        """
        params = {
            "select": "bateau, date_passage, fermeture_a_la_circulation, re_ouverture_a_la_circulation, type_de_fermeture, fermeture_totale",
            "where": "date_passage >= now() - interval '1 year'",
            "order_by": "date_passage ASC, fermeture_a_la_circulation ASC",
            "limit": str(limit),
        }

        LOGGER.debug("Fetching bridge data with limit=%d", limit)
        try:
            async with self._client.get(self._make_url(), params=params) as resp:
                LOGGER.debug("Received response with status=%d", resp.status)
                ret = await resp.json()
                if not isinstance(ret, dict) or "results" not in ret:
                    LOGGER.error("Invalid response format from API")
                    raise ValueError("Invalid response format from API")
                result = ApiResponse.from_json(ret)
                LOGGER.info("Successfully fetched %d bridge records", len(result.results))
                return result
        except aiohttp.ClientError as e:
            LOGGER.error("Failed to fetch bridge data: %s", e)
            raise aiohttp.ClientError(f"Failed to fetch bridge data: {e}") from e
        except (ValueError, KeyError) as e:
            LOGGER.error("Failed to parse API response: %s", e)
            raise ValueError(f"Failed to parse API response: {e}") from e
