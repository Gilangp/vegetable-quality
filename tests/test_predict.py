"""
Test suite untuk endpoint API klasifikasi sayur.
"""

import os
import pytest
from fastapi.testclient import TestClient
from main import app
from pathlib import Path


client = TestClient(app)


class TestPredictEndpoint:
    """Test cases untuk endpoint /predict"""

    def test_predict_with_valid_image_utuh(self):
        """Test prediksi dengan gambar UTUH yang valid"""
        test_image_path = "dataset/train/utuh"
        
        if os.path.exists(test_image_path):
            images = [f for f in os.listdir(test_image_path) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
            
            if images:
                image_file = os.path.join(test_image_path, images[0])
                with open(image_file, 'rb') as f:
                    response = client.post(
                        "/api/v1/predict",
                        files={"file": (images[0], f, "image/jpeg")}
                    )
                
                assert response.status_code == 200
                data = response.json()
                assert "message" in data
                assert "data" in data
                assert "prediction" in data["data"]
                assert "confidence" in data["data"]
                assert data["data"]["prediction"] in ["Utuh", "Tidak Utuh"]
                assert 0 <= data["data"]["confidence"] <= 1

    def test_predict_with_valid_image_tidak_utuh(self):
        """Test prediksi dengan gambar TIDAK UTUH yang valid"""
        test_image_path = "dataset/train/tidak_utuh"
        
        if os.path.exists(test_image_path):
            images = [f for f in os.listdir(test_image_path) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
            
            if images:
                image_file = os.path.join(test_image_path, images[0])
                with open(image_file, 'rb') as f:
                    response = client.post(
                        "/api/v1/predict",
                        files={"file": (images[0], f, "image/jpeg")}
                    )
                
                assert response.status_code == 200
                data = response.json()
                assert "message" in data
                assert "data" in data
                assert "prediction" in data["data"]
                assert "confidence" in data["data"]
                assert data["data"]["prediction"] in ["Utuh", "Tidak Utuh"]
                assert 0 <= data["data"]["confidence"] <= 1

    def test_predict_invalid_file_type(self):
        """Test prediksi dengan tipe file tidak valid"""
        response = client.post(
            "/api/v1/predict",
            files={"file": ("test.txt", b"invalid", "text/plain")}
        )
        
        assert response.status_code == 400
        assert "Tipe file tidak valid" in response.json()["detail"]

    def test_predict_missing_file(self):
        """Test prediksi tanpa file"""
        response = client.post("/api/v1/predict")
        
        assert response.status_code == 422

    def test_predict_large_file(self):
        """Test prediksi dengan file terlalu besar"""
        # buat file dummy 11MB (lebih besar dari limit 10MB)
        large_file = b"x" * (11 * 1024 * 1024)
        
        response = client.post(
            "/api/v1/predict",
            files={"file": ("large.jpg", large_file, "image/jpeg")}
        )
        
        assert response.status_code == 413
        assert "Ukuran file terlalu besar" in response.json()["detail"]


class TestOtherEndpoints:
    """Test cases untuk endpoint lain"""

    def test_root_endpoint(self):
        """Test endpoint root /"""
        response = client.get("/")
        assert response.status_code == 200

    def test_vegetable_quality_endpoint(self):
        """Test endpoint /vq"""
        response = client.get("/vq")
        assert response.status_code == 200

    def test_swagger_docs(self):
        """Test Swagger UI tersedia"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()

    def test_redoc(self):
        """Test ReDoc tersedia"""
        response = client.get("/redoc")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
