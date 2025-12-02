from datetime import datetime
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional


class ResidentApprovalBase(BaseModel):
    status: str  # pending_approval, approved, rejected
    note: Optional[str] = None
    
    @field_validator('status')
    def validate_status(cls, v: str) -> str:
        valid_statuses = {"pending_approval", "approved", "rejected"}
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class ResidentApprovalUpdate(BaseModel):
    """Update approval status (approve/reject by RT/RW)"""
    status: str  # approved or rejected
    note: Optional[str] = None
    family_id: Optional[int] = None  # Optional - if not provided, will auto-create family from family_number
    
    @field_validator('status')
    def validate_status(cls, v: str) -> str:
        valid_statuses = {"approved", "rejected"}
        if v not in valid_statuses:
            raise ValueError(f'Status must be either "approved" or "rejected"')
        return v


class ResidentApprovalResponse(BaseModel):
    """Response for resident approval"""
    id: int
    resident_id: Optional[int]
    name: Optional[str]
    nik: Optional[str]
    gender: Optional[str]
    birth_place: Optional[str]
    birth_date: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    status: str
    note: Optional[str]
    approved_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ResidentApprovalListResponse(BaseModel):
    """Response for listing resident approvals"""
    id: int
    resident_id: Optional[int]
    name: Optional[str]
    nik: Optional[str]
    gender: Optional[str]
    status: str
    note: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
