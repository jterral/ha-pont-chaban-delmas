import pytest
from custom_components.pont_chaban_delmas.pont_chaban import PontChaban

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

async def test_fetch_data_returns_closures() -> None:
    # Arrange
    pont = PontChaban()

    # Act
    actual = await pont.fetch_data()

    # Assert
    assert actual is not None
    assert actual.total_count > 0
    assert len(actual.results) > 0
    assert len(actual.results) == 10

    item1 = actual.results[0]
    assert item1.bateau == "MAINTENANCE"
    assert item1.date_passage == "2025-01-19"
    assert item1.fermeture_a_la_circulation == "23:00"
    assert item1.re_ouverture_a_la_circulation == "05:00"
    assert item1.type_de_fermeture == "Totale"
    assert item1.fermeture_totale == "oui"

    await pont.close()
