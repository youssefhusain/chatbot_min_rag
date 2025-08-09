from fastapi.testclient import TestClient
from src.main import app
from src.helpers.config import Settings
from src.routers.base import welcome

def override_get_settings():
    return Settings(
        APP_NAME="Test App",
        APP_VERSION="1.0.0",
        OPENAI_API_KEY="test-key",
        FILE_ALLOWED_TYPES="txt,pdf",
        FILE_MAX_SIZE=1024,
        FILE_DEFAULT_CHUNK_SIZE=256
    )

app.dependency_overrides[welcome.__defaults__[0].dependency] = override_get_settings

client = TestClient(app)

def test_welcome_endpoint():
    response = client.get("/api/v1/")
    assert response.status_code == 200
