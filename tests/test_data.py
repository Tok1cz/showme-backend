# tests/test_data.py
import pytest
from unittest.mock import AsyncMock
from app.db import queries

@pytest.mark.asyncio
async def test_get_n_nearest_attractions_mock(monkeypatch):
    fake_data = [
        {
            "id": 1,
            "name": "Test Museum",
            "lat": 55.0,
            "lon": -3.0,
            "structure_type": "POINT",
            "distance_m": 10.0,
            "description": "A museum",
            "tags": {"tourism": "museum"},
        },
        {
            "id": 2,
            "name": "Test Park",
            "lat": 55.1,
            "lon": -3.1,
            "structure_type": "POLYGON",
            "distance_m": 20.0,
            "description": "A park",
            "tags": {"leisure": "park"},
        }
    ]
    async def fake_query(session, lat, lon, n, extra_where=""):
        return fake_data[:n]

    monkeypatch.setattr(queries, "get_n_nearest_attractions", fake_query)

    # Simulate a fake session object (not used here, but required by signature)
    class DummySession: pass
    session = DummySession()

    results = await queries.get_n_nearest_attractions(session, 55.0, -3.0, 2) # type: ignore
    assert isinstance(results, list)
    assert len(results) == 2
    for row in results:
        assert "id" in row
        assert "lat" in row
        assert "lon" in row
        assert "structure_type" in row
        assert row["structure_type"] in ("POINT", "POLYGON", "LINESTRING")
