import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app
from fastapi.testclient import TestClient

os.environ["APP_NAME"] = "Test App"
os.environ["APP_VERSION"] = "1.0.0"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["FILE_ALLOWED_TYPES"] = ".txt,.pdf"
os.environ["FILE_MAX_SIZE"] = "1024"
os.environ["FILE_DEFAULT_CHUNK_SIZE"] = "256"

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_welcome_endpoint():
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "Test App"
    assert data["app_version"] == "1.0.0"

