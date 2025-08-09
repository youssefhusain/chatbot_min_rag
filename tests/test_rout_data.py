import sys
import os
from io import BytesIO
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from routes.data import data_router
from helpers.config import Settings, get_settings
from controllers import DataController, ProjectController
from models import ResponseSignal

app = FastAPI()
app.include_router(data_router)
client = TestClient(app)


@pytest.fixture(autouse=True)
def override_dependencies(monkeypatch):
    # Override Settings
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

    # Mock DataController.validate_uploaded_file
    monkeypatch.setattr(DataController, "validate_uploaded_file", lambda self, file: (True, ResponseSignal.FILE_UPLOAD_SUCCESS.value))
    # Mock DataController.generate_unique_filepath
    monkeypatch.setattr(DataController, "generate_unique_filepath", lambda self, orig_file_name, project_id: (f"/tmp/{orig_file_name}", "fake_file_id"))
    # Mock ProjectController.get_project_path
    monkeypatch.setattr(ProjectController, "get_project_path", lambda self, project_id: "/tmp")

    yield
    app.dependency_overrides.clear()


def test_upload_data_success(tmp_path):
  
    file_content = b"Hello, this is test content."
    file_like = BytesIO(file_content)

    response = client.post(
        "/api/v1/data/upload/test_project",
        files={"file": ("test.txt", file_like, "text/plain")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["signal"] == ResponseSignal.FILE_UPLOAD_SUCCESS.value
    assert data["file_id"] == "fake_file_id"


def test_upload_data_invalid_file(monkeypatch):

    monkeypatch.setattr(DataController, "validate_uploaded_file", lambda self, file: (False, "INVALID_FILE"))

    file_like = BytesIO(b"Invalid file content")

    response = client.post(
        "/api/v1/data/upload/test_project",
        files={"file": ("bad.txt", file_like, "text/plain")}
    )

    assert response.status_code == 400
    data = response.json()
    assert data["signal"] == "INVALID_FILE"
