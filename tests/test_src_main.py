from fastapi.testclient import TestClient
import pytest

import main  

client = TestClient(main.app)

def test_main_import():
    assert main.app is not None

def test_root_endpoint():
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "app_version" in data
