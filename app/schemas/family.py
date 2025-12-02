from datetime import datetime
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List


class FamilyBase(BaseModel):
    family_number: str
    head_resident_id: Optional[int] = None
    
    @field_validator('family_number')
    def validate_family_number(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError('Family number cannot be empty')
        return v.strip()


class FamilyCreate(FamilyBase):
    pass


class FamilyUpdate(BaseModel):
    family_number: Optional[str] = None
    head_resident_id: Optional[int] = None
    
    @field_validator('family_number')
    def validate_family_number(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if v.strip() == "":
                raise ValueError('Family number cannot be empty')
            return v.strip()
        return v


class ResidentInFamily(BaseModel):
    """Resident info for family response"""
    id: int
    name: str
    nik: str
    gender: Optional[str] = None
    status: Optional[str] = None
    
    class Config:
        from_attributes = True


class FamilyResponse(FamilyBase):
    """Response for family"""
    id: int
    family_number: str
    head_resident_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    residents: Optional[List[ResidentInFamily]] = []
    
    class Config:
        from_attributes = True


class FamilyListResponse(BaseModel):
    """Response for listing families"""
    id: int
    family_number: str
    head_resident_id: Optional[int]
    resident_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
