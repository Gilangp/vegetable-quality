from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routes import residents, auth, resident_approval, family, income, house, users
import routes.prediction as prediction_router
import os

BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
VIEWS_DIRECTORY = os.path.join(BASE_DIRECTORY, "views")

app = FastAPI(
    title="Pengujian Deteksi Keutuhan Sayur",
    version="1.0.0",
    description="API untuk klasifikasi keutuhan sayur (Utuh/Tidak Utuh) menggunakan MobileNetV2",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/assets", StaticFiles(directory=VIEWS_DIRECTORY, html=True), name="views")

@app.get("/", response_class=FileResponse)
async def root():
    """
    Halaman utama untuk melakukan pengujian deteksi keutuhan sayur.
    """
    return FileResponse(os.path.join(VIEWS_DIRECTORY, "html/index.html"))

@app.get("/vq", response_class=FileResponse)
async def vegetable_quality():
    """
    Halaman untuk menampilkan kualitas sayur.
    """
    return FileResponse(os.path.join(VIEWS_DIRECTORY, "html/vegetable-quality.html"))

app.include_router(auth.router)
app.include_router(prediction_router.router)
app.include_router(residents.router)
app.include_router(resident_approval.router)
app.include_router(family.router)
app.include_router(income.router)
app.include_router(house.router)
app.include_router(users.router)

if __name__ == "__main__":
    import uvicorn
    print("[INFO] Starting Uvicorn server on http://localhost:8000")
    uvicorn.run(app, host="localhost", port=8000)