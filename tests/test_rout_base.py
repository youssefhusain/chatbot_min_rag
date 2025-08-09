import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from routes.base import base_router 

import pytest



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
بحيث يناسب 
from fastapi import FastAPI, APIRouter, Depends
import os
from helpers.config import get_settings, Settings

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)

@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):

    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION

    return {
        "app_name": app_name,
        "app_version": app_version,
    }
