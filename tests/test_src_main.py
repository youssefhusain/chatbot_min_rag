from fastapi.testclient import TestClient
from main import app
client = TestClient(app)
def test_main_root():
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "app_version" in data

def test_main_data_upload(tmp_path):
    file_content = b"sample data"
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(file_content)

    with open(test_file, "rb") as f:
        response = client.post(
            "/api/v1/data/upload/123",
            files={"file": ("test.txt", f, "text/plain")}
        )

    assert response.status_code == 200
    data = response.json()
    assert "signal" in data
    assert "file_id" in data
