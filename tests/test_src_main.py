from fastapi.testclient import TestClient
from fastapi import FastAPI, APIRouter, Depends
from helpers.config import get_settings, Settings

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)

@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):
    return {
        "app_name": app_settings.APP_NAME,
        "app_version": app_settings.APP_VERSION,
    }

app = FastAPI()
app.include_router(base_router)

client = TestClient(app)

def test_welcome_endpoint():
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "app_version" in data
