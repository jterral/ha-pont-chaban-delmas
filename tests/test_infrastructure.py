# tests/test_infrastructure.py
from datetime import timedelta
from zoneinfo import ZoneInfo

import pytest

from custom_components.pont_chaban_delmas.infrastructure import (
    ODataClosureDTO,
    dto_to_domain,
)

EUROPE_PARIS = ZoneInfo("Europe/Paris")


@pytest.fixture
def json_record_fields():
    # Structure often returned by the API (record.fields)
    return {
        "record": {
            "fields": {
                "bateau": "MAINTENANCE",
                "date_passage": "2025-01-19",
                "fermeture_a_la_circulation": "23:00",
                "re_ouverture_a_la_circulation": "05:00",
                "type_de_fermeture": "Totale",
                "fermeture_totale": "oui",
            }
        }
    }


@pytest.fixture
def json_flat_same_day():
    # Flat structure, same-day closure (no midnight crossing)
    return {
        "bateau": "SILVER DAWN",
        "date_passage": "2025-04-08",
        "fermeture_a_la_circulation": "16:34",
        "re_ouverture_a_la_circulation": "17:57",
        "type_de_fermeture": "Totale",
        "fermeture_totale": "oui",
    }


def test_dto_from_json_record_fields(json_record_fields):
    dto = ODataClosureDTO.from_json(json_record_fields)
    assert dto.bateau == "MAINTENANCE"
    assert dto.date_passage == "2025-01-19"
    assert dto.fermeture_a_la_circulation == "23:00"
    assert dto.re_ouverture_a_la_circulation == "05:00"
    assert dto.type_de_fermeture == "Totale"
    assert dto.fermeture_totale == "oui"


def test_dto_from_json_flat(json_flat_same_day):
    dto = ODataClosureDTO.from_json(json_flat_same_day)
    assert dto.bateau == "SILVER DAWN"
    assert dto.date_passage == "2025-04-08"
    assert dto.fermeture_a_la_circulation == "16:34"
    assert dto.re_ouverture_a_la_circulation == "17:57"


def test_dto_to_domain_cross_midnight(json_record_fields):
    # 2025-01-19 23:00 → 2025-01-20 05:00 (Europe/Paris)
    dto = ODataClosureDTO.from_json(json_record_fields)
    domain = dto_to_domain(dto)

    # Basic mapping
    assert domain.boat == "MAINTENANCE"
    assert domain.is_total is True
    assert domain.closure_type == "Totale"

    # Start/end must be timezone-aware UTC
    assert domain.start_utc.tzinfo is not None
    assert domain.end_utc.tzinfo is not None
    assert domain.end_utc > domain.start_utc

    # Duration should be exactly 6 hours
    assert domain.duration() == timedelta(hours=6)

    # Local dates: start on 19th, end on 20th (Paris)
    start_local = domain.start_utc.astimezone(EUROPE_PARIS)
    end_local = domain.end_utc.astimezone(EUROPE_PARIS)
    assert start_local.date().isoformat() == "2025-01-19"
    assert end_local.date().isoformat() == "2025-01-20"
    assert start_local.strftime("%H:%M") == "23:00"
    assert end_local.strftime("%H:%M") == "05:00"


def test_dto_to_domain_same_day(json_flat_same_day):
    # 2025-04-08 16:34 → 17:57 (same day, Europe/Paris)
    dto = ODataClosureDTO.from_json(json_flat_same_day)
    domain = dto_to_domain(dto)

    # Sanity
    assert domain.boat == "SILVER DAWN"
    assert domain.end_utc > domain.start_utc
    # Duration 1h23
    assert domain.duration() == timedelta(hours=1, minutes=23)

    # Local times preserved
    start_local = domain.start_utc.astimezone(EUROPE_PARIS)
    end_local = domain.end_utc.astimezone(EUROPE_PARIS)
    assert start_local.date().isoformat() == "2025-04-08"
    assert end_local.date().isoformat() == "2025-04-08"
    assert start_local.strftime("%H:%M") == "16:34"
    assert end_local.strftime("%H:%M") == "17:57"
