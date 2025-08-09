import sys
import os
from io import BytesIO
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from routes.data import data_router
from helpers.config import Settings, get_settings
import routes.data as data_module

app = FastAPI()
app.include_router(data_router)
client = TestClient(app)


@pytest.fixture(autouse=True)
def override_dependencies(monkeypatch):
    # override settings
    def _override_settings():
        return Settings(
            APP_NAME="TestApp",
            APP_VERSION="1.0.0",
            OPENAI_API_KEY="fake_key",
            FILE_ALLOWED_TYPES=[".txt"],
            FILE_MAX_SIZE=5_000_000,
            FILE_DEFAULT_CHUNK_SIZE=1024
        )
    app.dependency_overrides[get_settings] = _override_settings


    class FakeDataController:
        def validate_uploaded_file(self, file):
            return True, "OK"
        def generate_unique_filepath(self, orig_file_name, project_id):
            return f"/tmp/{orig_file_name}", "fake_file_id"

    class FakeProjectController:
        def get_project_path(self, project_id):
            return "/tmp"

    monkeypatch.setattr(data_module, "DataController", FakeDataController)
    monkeypatch.setattr(data_module, "ProjectController", FakeProjectController)

    yield
    app.dependency_overrides.clear()


def test_upload_data_success():
    file_like = BytesIO(b"Hello")
    response = client.post(
        "/api/v1/data/upload/project123",
        files={"file": ("test.txt", file_like, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["signal"] == "OK"
    assert data["file_id"] == "fake_file_id"
