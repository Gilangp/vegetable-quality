from fastapi.testclient import TestClient
from main import app
from typing import LiteralString
import os

client = TestClient(app)

def test_predict():
    """
    Tes fungsional (*end-to-end*) untuk *endpoint* `/predict`.
    """
    dataset_path: LiteralString = os.path.join("data", "*.jpg")
    assert os.path.exists(
        dataset_path), f"Berkas dataset tidak ditemukan pada {dataset_path}"

    with open(dataset_path, "rb") as dataset_file:
        response = client.post("/predict", files={"file": dataset_file})

    if response.status_code != 200:
        print(f"Pengujian gagal dengan status kode {response.status_code}.")
        print(response.json())

    assert response.status_code == 200