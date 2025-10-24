import asyncio
import pytest
import aiohttp

from custom_components.pont_chaban_delmas.infrastructure import (
    OdataClient,
    dto_to_domain,
)

pytestmark = pytest.mark.asyncio

async def test_fetch_closures_real_api():
    async with aiohttp.ClientSession() as session:
        client = OdataClient(session)
        dtos = await client.fetch_closures(limit=5)

    # Vérif basique sur la structure
    assert isinstance(dtos, list)
    assert len(dtos) > 0

    # Conversion domaine
    closures = [dto_to_domain(d) for d in dtos]
    assert closures[0].boat is not None
    assert closures[0].start_utc.tzinfo is not None
    assert closures[0].end_utc > closures[0].start_utc

    # Debug : affiche la première fermeture
    print("First closure:", closures[0])
