# test_app.py
import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from helpers.config import Settings
from main import base_router  


def get_test_settings():
    return Settings(APP_NAME="Test App", APP_VERSION="1.0.0")

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(base_router)
    return app

@pytest.mark.asyncio
async def test_welcome(app, monkeypatch):
    from helpers import config
    monkeypatch.setattr(config, "get_settings", get_test_settings)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "Test App"
    assert data["app_version"] == "1.0.0"
