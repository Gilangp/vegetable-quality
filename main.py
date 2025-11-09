from fastapi import FastAPI, File, HTTPException, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from models.prediction import SuccessResponse
from services.analyze import Analyze
import os

BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
VIEWS_DIRECTORY = os.path.join(BASE_DIRECTORY, "views")

analyzer = Analyze()
app = FastAPI(title="Pengujian Deteksi Keutuhan Sayur", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/assets", StaticFiles(directory=VIEWS_DIRECTORY, html=True), name="views")

@app.post("/predict", response_model=SuccessResponse)
async def predict(file: UploadFile = File(..., alias="file")):
    """
    URL untuk pengujian mendeteksi keutuhan sayur.
    """
    try:
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipe gambar tidak valid, harap unggah JPG atau PNG.")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"data": analyzer.analyze(await file.read()).model_dump()})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/", response_class=FileResponse)
async def root():
    """
    Halaman utama untuk melakukan pengujian deteksi keutuhan sayur.
    """
    return FileResponse(os.path.join(VIEWS_DIRECTORY, "index.html"))