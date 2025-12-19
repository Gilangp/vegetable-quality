from datetime import datetime, date
from pydantic import BaseModel, field_validator, ConfigDict, field_serializer
from typing import Optional, Union


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
    resident_id: Optional[int] = None
    name: Optional[str] = None
    nik: Optional[str] = None
    gender: Optional[str] = None
    birth_place: Optional[str] = None
    birth_date: Optional[Union[str, date]] = None  # Accept both string and date
    phone: Optional[str] = None
    address: Optional[str] = None
    family_number: Optional[str] = None
    status: str
    note: Optional[str] = None
    approved_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_serializer('birth_date', when_used='json')
    def serialize_birth_date(self, value: Union[str, date, None]) -> Optional[str]:
        """Convert date to ISO string format"""
        if value is None:
            return None
        if isinstance(value, date):
            return value.isoformat()
        return str(value)
    
    class Config:
        from_attributes = True


class ResidentApprovalListResponse(BaseModel):
    """Response for listing resident approvals"""
    id: int
    resident_id: Optional[int]
    name: Optional[str]
    nik: Optional[str]
    gender: Optional[str]
    family_number: Optional[str]
    status: str
    note: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
