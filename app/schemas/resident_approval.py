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
    family_id: Optional[int] = None  # Required if status=approved
    
    @field_validator('status')
    def validate_status(cls, v: str) -> str:
        valid_statuses = {"approved", "rejected"}
        if v not in valid_statuses:
            raise ValueError(f'Status must be either "approved" or "rejected"')
        return v
    
    @field_validator('family_id')
    def validate_family_id(cls, v: Optional[int], info) -> Optional[int]:
        if info.data.get('status') == 'approved' and not v:
            raise ValueError('family_id is required when approving')
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
    updated_at: datetime
    
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
    updated_at: datetime
    
    class Config:
        from_attributes = True
