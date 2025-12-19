from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class FamilyMutationBase(BaseModel):
    family_id: int
    mutation_type: Optional[str] = None
    description: Optional[str] = None
    alamat_lama: Optional[str] = None
    alamat_baru: Optional[str] = None


class FamilyMutationCreate(FamilyMutationBase):
    pass


class FamilyMutationResponse(FamilyMutationBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FamilyMutationListResponse(BaseModel):
    id: int
    family_id: int
    mutation_type: Optional[str] = None
    description: Optional[str] = None
    alamat_lama: Optional[str] = None
    alamat_baru: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
