import sys, os
import pytest
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse
from starlette import status

# نضيف src للمسار عشان الاستيرادات تشتغل
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from routes.data import data_router
from helpers.config import get_settings, Settings
from models import ResponseSignal

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
    file_like = BytesIO(file_content)

    with patch("routes.data.DataController") as MockDC, \
         patch("routes.data.ProjectController") as MockPC, \
         patch("aiofiles.open", AsyncMock()) as mock_aio_open:

        mock_dc = MockDC.return_value
        mock_dc.validate_uploaded_file.return_value = (True, None)
        mock_dc.generate_unique_filepath.return_value = (str(tmp_path / "out.txt"), "file123")

        MockPC.return_value.get_project_path.return_value = str(tmp_path)

        response = client.post(
            "/api/v1/data/upload/proj1",
            files={"file": ("test.txt", file_like, "text/plain")}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["signal"] == ResponseSignal.FILE_UPLOAD_SUCCESS.value
        assert data["file_id"] == "file123"
        mock_aio_open.assert_called_once()

def test_upload_data_invalid_file():
    file_like = BytesIO(b"whatever")

    with patch("routes.data.DataController") as MockDC:
        mock_dc = MockDC.return_value
        mock_dc.validate_uploaded_file.return_value = (False, ResponseSignal.FILE_UPLOAD_FAILED.value)

        response = client.post(
            "/api/v1/data/upload/proj1",
            files={"file": ("bad.txt", file_like, "text/plain")}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["signal"] == ResponseSignal.FILE_UPLOAD_FAILED.value

def test_upload_data_exception_during_write(tmp_path):
    file_like = BytesIO(b"abc")

    async def raise_io(*args, **kwargs):
        raise IOError("Disk full")

    with patch("routes.data.DataController") as MockDC, \
         patch("routes.data.ProjectController") as MockPC, \
         patch("aiofiles.open", side_effect=raise_io):

        mock_dc = MockDC.return_value
        mock_dc.validate_uploaded_file.return_value = (True, None)
        mock_dc.generate_unique_filepath.return_value = (str(tmp_path / "o.txt"), "fid")

        MockPC.return_value.get_project_path.return_value = str(tmp_path)

        response = client.post(
            "/api/v1/data/upload/proj1",
            files={"file": ("test.txt", file_like, "text/plain")}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["signal"] == ResponseSignal.FILE_UPLOAD_FAILED.value
