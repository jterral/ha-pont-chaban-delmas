"""Infrastructure code to access the OData API of Bordeaux Métropole for Pont Chaban-Delmas."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any
import aiohttp
from zoneinfo import ZoneInfo
from homeassistant.util import dt as dt_util

from .domain import BridgeClosure

EUROPE_PARIS = ZoneInfo("Europe/Paris")

API_BASE = "https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/previsions_pont_chaban/records"
USER_AGENT = "ha-pont-chaban-delmas/0.1"

@dataclass(frozen=True)
class ODataClosureDTO:
    bateau: str | None
    date_passage: str
    fermeture_a_la_circulation: str
    re_ouverture_a_la_circulation: str
    type_de_fermeture: str | None
    fermeture_totale: str | None

    @staticmethod
    def from_json(obj: Dict[str, Any]) -> "ODataClosureDTO":
        fields = obj.get("record", {}).get("fields") or obj
        return ODataClosureDTO(
            bateau=fields.get("bateau"),
            date_passage=fields["date_passage"],
            fermeture_a_la_circulation=fields["fermeture_a_la_circulation"],
            re_ouverture_a_la_circulation=fields["re_ouverture_a_la_circulation"],
            type_de_fermeture=fields.get("type_de_fermeture"),
            fermeture_totale=fields.get("fermeture_totale"),
        )

def _combine_local(date_str: str, hm: str) -> datetime:
    """Combine 'YYYY-MM-DD' + 'HH:MM' en datetime tz-aware Europe/Paris."""
    d = date.fromisoformat(date_str)
    h, m = hm.split(":")
    t = time(int(h), int(m))
    return datetime.combine(d, t, tzinfo=EUROPE_PARIS)

def dto_to_domain(dto: ODataClosureDTO) -> BridgeClosure:
    start_local = _combine_local(dto.date_passage, dto.fermeture_a_la_circulation)
    end_local = _combine_local(dto.date_passage, dto.re_ouverture_a_la_circulation)

    # Si l'heure de réouverture est "après minuit" (ex: 23:00 → 05:00), on passe au lendemain
    if end_local <= start_local:
        end_local = end_local + timedelta(days=1)

    start_utc = dt_util.as_utc(start_local)
    end_utc = dt_util.as_utc(end_local)

    return BridgeClosure(
        boat=(dto.bateau or "").strip(),
        start_utc=start_utc,
        end_utc=end_utc,
        closure_type=(dto.type_de_fermeture or "").strip() or None,
        is_total=(dto.fermeture_totale or "").strip().lower() == "oui",
    )

class OdataClient:
    def __init__(self, session: aiohttp.ClientSession | None = None):
        self._session = session

    async def fetch_closures(self, limit: int = 50) -> List[ODataClosureDTO]:
        params = {
            "select": "bateau, date_passage, fermeture_a_la_circulation, re_ouverture_a_la_circulation, type_de_fermeture, fermeture_totale",
            "where": "date_passage >= now() - interval '1 year'",  # garde large, côté domaine on filtre le futur
            "order_by": "date_passage ASC, fermeture_a_la_circulation ASC",
            "limit": str(limit),
        }
        headers = {"User-Agent": USER_AGENT}
        close_session = False
        session = self._session
        if session is None:
            session = aiohttp.ClientSession(headers=headers)
            close_session = True
        else:
            session.headers.update(headers)

        try:
            async with session.get(API_BASE, params=params, timeout=30) as resp:
                resp.raise_for_status()
                payload = await resp.json()
        finally:
            if close_session:
                await session.close()

        raw_results = payload.get("results") or []
        return [ODataClosureDTO.from_json(r) for r in raw_results]
