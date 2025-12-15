"""API client for Pont Chaban-Delmas bridge data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import TracebackType
from typing import List, Optional, Type

import aiohttp
from homeassistant.util import dt as dt_util

from .const import LOGGER
from .domain import BridgeClosure


@dataclass(frozen=True)
class ApiBridgeResponse:
    """Response data for a single bridge passage event (DTO).

    Attributes:
        bateau: Name of the boat passing through.
        date_passage: Date of the passage (YYYY-MM-DD).
        fermeture_a_la_circulation: Road closure time (HH:MM).
        re_ouverture_a_la_circulation: Road reopening time (HH:MM).
        type_de_fermeture: Type of closure.
        fermeture_totale: Whether it's a total closure (oui/non).
    """

    bateau: str
    date_passage: str
    fermeture_a_la_circulation: str
    re_ouverture_a_la_circulation: str
    type_de_fermeture: str
    fermeture_totale: str

    @classmethod
    def from_json(cls, data: dict) -> ApiBridgeResponse:
        """Create a BridgeResponse from JSON data.

        Parameters:
            data: Dictionary containing bridge response fields.

        Returns:
            BridgeResponse: Instance created from JSON data.
        """
        return cls(**data)


@dataclass(frozen=True)
class ApiResponse:
    """API response containing bridge passage records (DTO).

    Attributes:
        total_count: Total number of records available.
        results: List of bridge passage events.
    """

    total_count: int
    results: List[ApiBridgeResponse]

    @classmethod
    def from_json(cls, data: dict) -> ApiResponse:
        """Create an ApiResponse from JSON data.

        Parameters:
            data: Dictionary containing API response with 'total_count' and 'results'.

        Returns:
            ApiResponse: Instance with parsed bridge responses.
        """
        results = [ApiBridgeResponse.from_json(item) for item in data["results"]]

        return cls(
            total_count=data["total_count"],
            results=results,
        )


class PontChabanRepository:
    """Repository for accessing Pont Chaban bridge data from the API."""

    BASE_ADDRESS = "https://datahub.bordeaux-metropole.fr"

    def __init__(self) -> None:
        """Initialize the Pont Chaban repository."""
        LOGGER.debug("Initializing PontChabanRepository")
        self._base_address = self.BASE_ADDRESS
        self._client = aiohttp.ClientSession(raise_for_status=True)

    async def close(self) -> None:
        """Close the HTTP client session."""
        LOGGER.debug("Closing PontChabanRepository")
        await self._client.close()

    async def __aenter__(self) -> PontChabanRepository:
        """Context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        """Context manager exit."""
        await self.close()
        return None

    def _make_url(self) -> str:
        """Build the API endpoint URL."""
        return (
            self._base_address
            + "/api/explore/v2.1/catalog/datasets/previsions_pont_chaban/records"
        )

    async def get_upcoming_closures(self, limit: int = 20) -> list[BridgeClosure]:
        """Fetch upcoming bridge closures from the API.

        Parameters:
            limit: Maximum number of records to fetch (default: 20).

        Returns:
            list[BridgeClosure]: List of upcoming bridge closures (domain objects).

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

        LOGGER.debug("Fetching bridge closures with limit=%d", limit)
        try:
            async with self._client.get(self._make_url(), params=params) as resp:
                LOGGER.debug("Received response with status=%d", resp.status)
                ret = await resp.json()
                if not isinstance(ret, dict) or "results" not in ret:
                    LOGGER.error("Invalid response format from API")
                    raise ValueError("Invalid response format from API")

                api_response = ApiResponse.from_json(ret)
                closures = [self._to_domain(item) for item in api_response.results]
                LOGGER.info("Successfully fetched %d bridge closures", len(closures))
                return closures

        except aiohttp.ClientError as e:
            LOGGER.error("Failed to fetch bridge closures: %s", e)
            raise aiohttp.ClientError(f"Failed to fetch bridge closures: {e}") from e
        except (ValueError, KeyError) as e:
            LOGGER.error("Failed to parse API response: %s", e)
            raise ValueError(f"Failed to parse API response: {e}") from e

    def _to_domain(self, dto: ApiBridgeResponse) -> BridgeClosure:
        """Convert a DTO to a domain object.

        Parameters:
            dto: Data transfer object from API.

        Returns:
            BridgeClosure: Domain object representing a bridge closure.

        Raises:
            ValueError: If datetime parsing fails.
        """
        try:
            start_utc = self._parse_datetime(
                dto.date_passage, dto.fermeture_a_la_circulation
            )
            end_utc = self._parse_datetime(
                dto.date_passage, dto.re_ouverture_a_la_circulation
            )

            # Handle midnight crossing
            if end_utc <= start_utc:
                end_utc = end_utc.replace(day=end_utc.day + 1)

            return BridgeClosure(
                boat=dto.bateau or "N/A",
                start_utc=start_utc,
                end_utc=end_utc,
                closure_type=dto.type_de_fermeture or None,
                is_total=(dto.fermeture_totale or "").strip().lower() == "oui",
            )
        except Exception as e:
            LOGGER.error("Failed to convert DTO to domain: %s", e)
            raise ValueError(f"Failed to convert bridge closure data: {e}") from e

    @staticmethod
    def _parse_datetime(date_str: str, time_str: str) -> datetime:
        """Parse date and time strings into a UTC datetime.

        Parameters:
            date_str: Date string in YYYY-MM-DD format.
            time_str: Time string in HH:MM format.

        Returns:
            datetime: UTC datetime object.

        Raises:
            ValueError: If parsing fails.
        """
        try:
            dt = datetime.fromisoformat(f"{date_str}T{time_str}:00")
            return dt.replace(tzinfo=dt_util.UTC)
        except Exception as e:
            raise ValueError(f"Invalid datetime format: {date_str} {time_str}") from e
