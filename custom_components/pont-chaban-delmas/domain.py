"""Domain models for pont-chaban-delmas integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict
from homeassistant.util import dt as dt_util

@dataclass(frozen=True)
class BridgeClosure:
    boat: str
    start_utc: datetime   # timezone-aware, UTC
    end_utc: datetime     # timezone-aware, UTC
    closure_type: str | None = None
    is_total: bool | None = None

    def duration(self) -> timedelta:
        return self.end_utc - self.start_utc

    def is_future(self, now_utc: datetime | None = None) -> bool:
        now_utc = now_utc or dt_util.utcnow()
        return self.end_utc > now_utc

    def is_today_local(self) -> bool:
        local_start = dt_util.as_local(self.start_utc)
        return local_start.date() == dt_util.as_local(dt_util.utcnow()).date()

    def is_tomorrow_local(self) -> bool:
        local_start = dt_util.as_local(self.start_utc).date()
        today = dt_util.as_local(dt_util.utcnow()).date()
        return local_start == (today + timedelta(days=1))

    def to_ha_attributes(self) -> Dict[str, str]:
        return {
            "boat": self.boat,
            "start": dt_util.as_local(self.start_utc).isoformat(),
            "end": dt_util.as_local(self.end_utc).isoformat(),
            "duration": str(self.duration()).split(".")[0],
            "type_de_fermeture": self.closure_type or "",
            "fermeture_totale": "oui" if self.is_total else "non",
            "is_today": self.is_today_local(),
            "is_tomorrow": self.is_tomorrow_local(),
        }
