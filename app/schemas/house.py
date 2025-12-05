from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional


class HouseBase(BaseModel):
    house_number: Optional[str] = None
    address: Optional[str] = None
    rt: Optional[str] = None
    rw: Optional[str] = None

    @field_validator('house_number')
    def validate_house_number(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() == "":
            raise ValueError('house_number cannot be empty string')
        return v


class HouseCreate(HouseBase):
    pass


class HouseUpdate(BaseModel):
    house_number: Optional[str] = None
    address: Optional[str] = None
    rt: Optional[str] = None
    rw: Optional[str] = None
    status: Optional[str] = None


class HouseResponse(BaseModel):
    id: int
    house_number: Optional[str] = None
    address: Optional[str] = None
    rt: Optional[str] = None
    rw: Optional[str] = None
    status: Optional[str] = None
    resident_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
