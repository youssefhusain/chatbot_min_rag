import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.responses import JSONResponse
from starlette import status
from routes.data import upload_data
from models import ResponseSignal


@pytest.mark.asyncio
async def test_upload_data_success():
    mock_file = AsyncMock()
    mock_file.filename = "test.txt"
    mock_file.read = AsyncMock(side_effect=[b"some content", b""])

    mock_settings = MagicMock()
    mock_settings.FILE_DEFAULT_CHUNK_SIZE = 1024

    with patch("routes.data.DataController") as MockDataController, \
         patch("routes.data.ProjectController") as MockProjectController, \
         patch("aiofiles.open", AsyncMock()) as mock_aio_open:
        
        mock_data_ctrl = MockDataController.return_value
        mock_data_ctrl.validate_uploaded_file.return_value = (True, None)
        mock_data_ctrl.generate_unique_filepath.return_value = ("fake/path/test.txt", "file123")

        MockProjectController.return_value.get_project_path.return_value = "fake/project/path"

        response = await upload_data("project1", mock_file, app_settings=mock_settings)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_200_OK
        body = response.body.decode()
        assert ResponseSignal.FILE_UPLOAD_SUCCESS.value in body
        assert "file123" in body
        mock_aio_open.assert_called_once()


@pytest.mark.asyncio
async def test_upload_data_invalid_file():
    mock_file = AsyncMock()
    mock_file.filename = "bad.txt"
    mock_settings = MagicMock()

    with patch("routes.data.DataController") as MockDataController:
        mock_data_ctrl = MockDataController.return_value
        mock_data_ctrl.validate_uploaded_file.return_value = (False, ResponseSignal.FILE_UPLOAD_FAILED.value)

        response = await upload_data("project1", mock_file, app_settings=mock_settings)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ResponseSignal.FILE_UPLOAD_FAILED.value in response.body.decode()


@pytest.mark.asyncio
async def test_upload_data_exception_during_write():
    mock_file = AsyncMock()
    mock_file.filename = "test.txt"
    mock_file.read = AsyncMock(side_effect=[b"data", b""])

    mock_settings = MagicMock()
    mock_settings.FILE_DEFAULT_CHUNK_SIZE = 1024

    async def mock_open(*args, **kwargs):
        raise IOError("Disk error")

    with patch("routes.data.DataController") as MockDataController, \
         patch("routes.data.ProjectController") as MockProjectController, \
         patch("aiofiles.open", side_effect=mock_open):
        
        mock_data_ctrl = MockDataController.return_value
        mock_data_ctrl.validate_uploaded_file.return_value = (True, None)
        mock_data_ctrl.generate_unique_filepath.return_value = ("fake/path/test.txt", "file123")

        MockProjectController.return_value.get_project_path.return_value = "fake/project/path"

        response = await upload_data("project1", mock_file, app_settings=mock_settings)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ResponseSignal.FILE_UPLOAD_FAILED.value in response.body.decode()
