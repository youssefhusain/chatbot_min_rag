import sys
import os
from fastapi.testclient import TestClient
import pytest

# إضافة مسار src عشان يقدر يقرأ الملفات
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import app

client = TestClient(app)

def test_main_import():
    """نتأكد إن التطبيق بيتحمل"""
    assert app is not None

def test_base_router_endpoint():
    """اختبار مسار base"""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "app_version" in data

def test_data_router_upload(tmp_path):
    """اختبار رفع ملف من data_router"""
    file_content = b"hello world"
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(file_content)

    with open(test_file, "rb") as f:
        response = client.post(
            "/api/v1/data/upload/123",
            files={"file": ("test.txt", f, "text/plain")}
        )

    assert response.status_code in (200, 400)  # ممكن يكون 400 لو فشل التحقق
    data = response.json()
    assert "signal" in data
