from typing import Any
from app.controllers.prediction import PredictionController
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/predict", tags=["Prediction"])

@router.post("/")
async def predict_vegetable(file: UploadFile = File(...)):
    """
    Endpoint untuk memprediksi keutuhan sayur dari gambar yang di-upload.

    **Request:**
    - file: Gambar sayur (.jpg, .png, atau .bmp)

    **Response:**
    - prediction: "Utuh" atau "Tidak Utuh"
    - confidence: Confidence score (0-1)
    - class_probabilities: Probabilitas untuk setiap kelas

    **Example:**
    ```json
    {
        "message": "Analisis gambar berhasil",
        "data": {
            "prediction": "Utuh",
            "confidence": 0.9542,
            "class_probabilities": {
                "utuh": 0.9542,
                "tidak_utuh": 0.0458
            }
        }
    }
    ```
    """
    # Validasi tipe file
    PredictionController.validate_file(str(file.content_type))
    
    # Baca file contents
    contents = await file.read()
    
    # Validasi ukuran file
    PredictionController.validate_file_size(len(contents))
    
    # Jalankan prediksi
    result: dict[str, Any] = PredictionController.predict(contents, str(file.filename))
    return JSONResponse(status_code=200, content=result)