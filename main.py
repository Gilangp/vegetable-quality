from app.controllers.resident import Resident as ResidentController
from app.models.residents import Citizen as CitizenSchema
from app.routes.prediction import router as prediction_router
from config.database import get_db
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os

BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
VIEWS_DIRECTORY = os.path.join(BASE_DIRECTORY, "views")

app = FastAPI(
    title="Pengujian Deteksi Keutuhan Sayur",
    version="1.0.0",
    description="API untuk klasifikasi keutuhan sayur (Utuh/Tidak Utuh) menggunakan MobileNetV2",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc UI
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/assets", StaticFiles(directory=VIEWS_DIRECTORY, html=True), name="views")

@app.get("/", response_class=FileResponse)
async def root():
    """
    Halaman utama untuk melakukan pengujian deteksi keutuhan sayur.
    """
    return FileResponse(os.path.join(VIEWS_DIRECTORY, "html/index.html"))

@app.get("/c", response_class=FileResponse)
async def citizen(db: Session = Depends(get_db)):
    """
    Endpoint untuk mengambil semua data citizen.
    """
    try:
        return FileResponse(os.path.join(VIEWS_DIRECTORY, "html/citizen.html"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/citizen", response_class=FileResponse)
async def create_citizen(data: CitizenSchema, db: Session = Depends(get_db)):
    """
    Endpoint untuk membuat data citizen baru.
    """
    try:
        return CitizenController(db).store(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/citizen/{nik}", response_class=FileResponse)
async def update_citizen(nik: int, data: CitizenSchema, db: Session = Depends(get_db)):
    """
    Endpoint untuk memperbarui data citizen berdasarkan NIK.
    """
    try:
        updated = CitizenController(db).update(nik, data)
        if not updated:
            raise HTTPException(status_code=404, detail="Citizen not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/citizen/{nik}", response_class=FileResponse)
async def delete_citizen(nik: int, db: Session = Depends(get_db)):
    """
    Endpoint untuk menghapus data citizen berdasarkan NIK.
    """
    try:
        destroyed = CitizenController(db).destroy(nik)
        if not destroyed:
            raise HTTPException(status_code=404, detail="Citizen not found")
        return destroyed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vq", response_class=FileResponse)
async def vegetable_quality():
    """
    Halaman untuk menampilkan kualitas sayur.
    """
    return FileResponse(os.path.join(VIEWS_DIRECTORY, "html/vegetable-quality.html"))


# prediction routes
app.include_router(prediction_router)