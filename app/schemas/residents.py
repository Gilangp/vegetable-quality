from datetime import date
from pydantic import BaseModel
from typing import Optional

class ResidentBase(BaseModel):
    nik: str
    name: str
    phone: Optional[str] = None
    birth_place: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    status: Optional[str] = None

class ResidentCreate(ResidentBase):
    family_id: int
    house_id: int

class ResidentUpdate(BaseModel):
    family_id: Optional[int] = None
    house_id: Optional[int] = None
    nik: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    birth_place: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    status: Optional[str] = None

class ResidentResponse(ResidentBase):
    id: int
    family_id: int
    house_id: int

    class Config:
        from_attributes = True