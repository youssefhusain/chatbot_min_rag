import sys
import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from routes.base import base_router
from helpers.config import Settings, get_settings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

app = FastAPI()
app.include_router(base_router)
client = TestClient(app)


@pytest.fixture(autouse=True)
def override_get_settings():
    # إنشاء نسخة مخصصة من Settings للاختبار
    def _override_settings():
        return Settings(APP_NAME="TestApp", APP_VERSION="1.0.0")
    app.dependency_overrides[get_settings] = _override_settings
    yield
    app.dependency_overrides.clear()


def test_welcome():
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "TestApp"
    assert data["app_version"] == "1.0.0"
