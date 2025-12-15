"""Domain models for Pont Chaban-Delmas integration."""

from __future__ import annotations

from homeassistant.util import dt as dt_util
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class BridgeClosure:
    """Represents a scheduled bridge closure event.

    Attributes:
        boat: Name of the boat causing the closure.
        start_utc: UTC datetime when the bridge closes.
        end_utc: UTC datetime when the bridge reopens.
        closure_type: Type of closure (e.g., "Totale", "Partielle").
        is_total: Whether it's a total closure.
    """

    boat: str
    start_utc: datetime
    end_utc: datetime
    closure_type: str | None
    is_total: bool

    def duration(self) -> timedelta:
        """Calculate the duration of the closure.

        Returns:
            timedelta: Duration between start and end times.
        """
        return self.end_utc - self.start_utc

    def is_active(self, now: datetime | None = None) -> bool:
        """Check if the closure is currently active.

        Parameters:
            now: Current time to check against (defaults to UTC now).

        Returns:
            bool: True if the closure is currently happening.
        """
        if now is None:
            now = dt_util.utcnow()

        return self.start_utc <= now < self.end_utc

    def is_upcoming(self, now: datetime | None = None) -> bool:
        """Check if the closure is in the future.

        Parameters:
            now: Current time to check against (defaults to UTC now).

        Returns:
            bool: True if the closure hasn't started yet.
        """
        if now is None:
            now = dt_util.utcnow()

        return self.start_utc > now
