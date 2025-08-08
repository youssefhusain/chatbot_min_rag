import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.routes.base import base_router
app = FastAPI()
app.include_router(base_router)

client = TestClient(app)

@pytest.fixture(autouse=True)
def set_env_vars():
    os.environ["APP_NAME"] = "TestApp"
    os.environ["APP_VERSION"] = "1.0.0"
    yield
    os.environ.pop("APP_NAME", None)
    os.environ.pop("APP_VERSION", None)

def test_welcome():
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "TestApp"
    assert data["app_version"] == "1.0.0"
