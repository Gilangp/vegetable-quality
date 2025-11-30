from fastapi.responses import FileResponse
from app.schemas.residents import ResidentCreate, ResidentUpdate, ResidentResponse
from app.controllers.resident import Resident as ResidentController
from config.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os

router = APIRouter(prefix="/residents", tags=["Residents"])

current_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(current_dir) if "routes" in current_dir else current_dir
VIEWS_DIRECTORY = os.path.join(PROJECT_ROOT, "views")

@router.get("/", response_class=FileResponse)
def residents_page():
    file_path = os.path.join(VIEWS_DIRECTORY, "html/residents.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found at {file_path}")
    return FileResponse(file_path)

@router.get("/data", response_model=List[ResidentResponse])
def get(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ResidentController(db).index(skip=skip, limit=limit)

@router.get("/{id}", response_model=ResidentResponse)
async def show(id: int, db: Session = Depends(get_db)):
    resident = ResidentController(db).show(id)
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found!")
    return resident

@router.post("/", response_model=ResidentResponse, status_code=status.HTTP_201_CREATED)
def store(data: ResidentCreate, db: Session = Depends(get_db)):
    return ResidentController(db).store(data)

@router.put("/{id}", response_model=ResidentResponse)
def update(id: int, data: ResidentUpdate, db: Session = Depends(get_db)):
    resident = ResidentController(db).update(id, data)
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found!")
    return resident

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def destroy(id: int, db: Session = Depends(get_db)):
    success = ResidentController(db).destroy(id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found!")
    return None