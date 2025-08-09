import sys
import os
import pytest
from fastapi.testclient import TestClient


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import app

client = TestClient(app)

def test_main_app_loads():
    assert app is not None
    assert app.title == "FastAPI"

def test_base_router_exists():
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "app_version" in data

def test_data_router_upload_endpoint_exists():
    response = client.post("/api/v1/data/upload/123", files={"file": ("test.txt", b"hello", "text/plain")})
    assert response.status_code in [200, 400]
