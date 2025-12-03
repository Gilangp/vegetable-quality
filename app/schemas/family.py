from datetime import datetime
from pydantic import BaseModel, field_validator, ConfigDict, Field
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
    house_id: Optional[int] = None
    house: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class FamilyResponse(FamilyBase):
    """Response for family"""
    id: int
    family_number: str
    head_resident_id: Optional[int]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    residents: List[ResidentInFamily] = Field(default_factory=list)
    head_resident: Optional[ResidentInFamily] = None

    model_config = ConfigDict(from_attributes=True)


class FamilyListResponse(BaseModel):
    """Response for listing families"""
    id: int
    family_number: str
    head_resident_id: Optional[int]
    head_resident: Optional[ResidentInFamily] = None
    resident_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Standard message response"""
    message: str
    model_config = ConfigDict(from_attributes=True)
