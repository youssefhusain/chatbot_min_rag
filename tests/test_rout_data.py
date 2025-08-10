import sys
import os
import types
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# ===== Mock للـ controllers =====
fake_controllers = types.ModuleType("controllers")

class FakeDataController:
    def validate_uploaded_file(self, file):
        return True, "FILE_UPLOAD_SUCCESS"

    def generate_unique_filepath(self, orig_file_name, project_id):
        return f"/tmp/{orig_file_name}", "fake_file_id"

class FakeProjectController:
    def get_project_path(self, project_id):
        return "/tmp"

class FakeProcessController:
    def __init__(self, project_id):
        self.project_id = project_id

    def get_file_content(self, file_id):
        return "some file content"

    def process_file_content(self, file_content, file_id, chunk_size, overlap_size):
        return [{"chunk": "part1"}, {"chunk": "part2"}]

fake_controllers.DataController = FakeDataController
fake_controllers.ProjectController = FakeProjectController
fake_controllers.ProcessController = FakeProcessController

sys.modules["controllers"] = fake_controllers
# ===== End Mock =====

from routes.data import data_router
from helpers.config import Settings, get_settings

app = FastAPI()
app.include_router(data_router)
client = TestClient(app)

@pytest.fixture(autouse=True)
def override_settings():
    def _override():
        return Settings(
            APP_NAME="TestApp",
            APP_VERSION="1.0.0",
            OPENAI_API_KEY="fake",
            FILE_ALLOWED_TYPES=[".txt"],
            FILE_MAX_SIZE=5_000_000,
            FILE_DEFAULT_CHUNK_SIZE=1024
        )
    app.dependency_overrides[get_settings] = _override
    yield
    app.dependency_overrides.clear()

def test_upload_data_success(tmp_path):
    file_content = b"hello world"
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(file_content)

    with open(test_file, "rb") as f:
        response = client.post(
            "/api/v1/data/upload/123",
            files={"file": ("test.txt", f, "text/plain")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["signal"].upper() == "FILE_UPLOAD_SUCCESS"
    assert data["file_id"] == "fake_file_id"

def test_upload_data_invalid_file(tmp_path):
    fake_controllers.DataController.validate_uploaded_file = lambda self, file: (False, "INVALID_FILE")

    test_file = tmp_path / "bad.txt"
    test_file.write_bytes(b"bad content")

    with open(test_file, "rb") as f:
        response = client.post(
            "/api/v1/data/upload/123",
            files={"file": ("bad.txt", f, "text/plain")}
        )

    assert response.status_code == 400
    data = response.json()
    assert data["signal"] == "INVALID_FILE"

def test_process_endpoint_success():
    payload = {
        "file_id": "fake_file_id",
        "chunk_size": 100,
        "overlap_size": 10
    }
    response = client.post("/api/v1/data/process/123", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["chunk"] == "part1"

def test_process_endpoint_failed():

    fake_controllers.ProcessController.process_file_content = lambda *args, **kwargs: None

    payload = {
        "file_id": "fake_file_id",
        "chunk_size": 100,
        "overlap_size": 10
    }
    response = client.post("/api/v1/data/process/123", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["signal"] == "PROCESSING_FAILED"
