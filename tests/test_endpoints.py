import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_healthcheck():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_nearest_pois(monkeypatch):
    # Patch the data layer to avoid hitting a real DB
    async def fake_get_n_nearest_attractions(session, lat, lon, n, extra_where=""):
        return [
            {
                "id": 1,
                "name": "Test Attraction",
                "description": "Testing",
                "tags": "tourism : museum",
                "structure_type": "POINT",
                "lat": 55.0,
                "lon": -3.0,
                "distance_m": 120.0,
            }
        ]

    # Patch in the real app
    from app.api.routes import pois

    monkeypatch.setattr(
        pois, "get_n_nearest_attractions", fake_get_n_nearest_attractions
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.get("/pois/nearest?lat=55&lon=-3&n=1")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert data[0]["name"] == "Test Attraction"
        assert data[0]["lat"] == 55.0
