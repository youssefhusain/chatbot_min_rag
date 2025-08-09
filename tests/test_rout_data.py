def test_upload_data(tmp_path):
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

    assert data["signal"].upper() in ["FILE_UPLOAD_SUCCESS", "OK"]
    assert "file_id" in data
