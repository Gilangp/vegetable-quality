from pydantic import BaseModel, Field
from typing import Literal

class PredictionData(BaseModel):
    """
    Berisi hasil prediksi dan skor kepercayaan.
    """
    confidence: float = Field(..., gt=0.0, le=1.0, examples=[0.95])
    prediction: Literal['Segar', 'Busuk'] = Field(..., examples=["Busuk", "Segar"])

class SuccessResponse(BaseModel):
    """Struktur respons API jika sukses menganalisis gambar."""
    message: str = Field(..., examples=["Analisis gambar berhasil"])
    data: PredictionData