import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from routes.base import base_router
from helpers.config import Settings, get_settings


app = FastAPI()
app.include_router(base_router)
client = TestClient(app)


@pytest.fixture(autouse=True)
def override_get_settings():
    def _override_settings():
        return Settings(
            APP_NAME="TestApp",
            APP_VERSION="1.0.0",
            OPENAI_API_KEY="fake_key",
            FILE_ALLOWED_TYPES=[".txt", ".pdf"],
            FILE_MAX_SIZE=5_000_000,
            FILE_DEFAULT_CHUNK_SIZE=1024,
            MONGODB_URL="mongodb://localhost:27017", 
            MONGODB_DATABASE="test_db"              
        )
    app.dependency_overrides[get_settings] = _override_settings
    yield
    app.dependency_overrides.clear()



def test_welcome():
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "TestApp"
    assert data["app_version"] == "1.0.0"
    

