from datetime import date
from pydantic import BaseModel, field_validator
from typing import Optional

class ResidentBase(BaseModel):
    nik: str
    name: str
    phone: Optional[str] = None
    birth_place: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    status: Optional[str] = None
    religion: Optional[str] = None
    blood_type: Optional[str] = None
    education: Optional[str] = None
    occupation: Optional[str] = None

    @field_validator('nik')
    def validate_nik(cls, v: str) -> str:
        if len(v) != 16 or not v.isdigit():
            raise ValueError('NIK must be a 16-digit number')
        return v
    
    @field_validator('birth_date')
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        if v and v > date.today():
            raise ValueError('Birth date cannot be in the future')
        return v
    
    @field_validator('name')
    def validate_name(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError('Name cannot be empty')
        return v
    
    @field_validator('gender')
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in {"Laki-laki", "Perempuan"}:
            raise ValueError('Gender must be either "Laki-laki" or "Perempuan"')
        return v
    
    @field_validator('phone')
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() == "":
            raise ValueError('Phone cannot be empty')
        return v
    
    @field_validator('status')
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() == "":
            raise ValueError('Status cannot be empty')
        return v
    
    @field_validator('blood_type')
    def validate_blood_type(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in {"A", "B", "AB", "O"}:
            pass
        return v

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
    religion: Optional[str] = None
    blood_type: Optional[str] = None
    education: Optional[str] = None
    occupation: Optional[str] = None

class ResidentResponse(ResidentBase):
    id: int
    family_id: int
    house_id: int

    class Config:
        from_attributes = True