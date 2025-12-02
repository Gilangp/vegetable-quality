from datetime import datetime
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from decimal import Decimal


class IncomeBase(BaseModel):
    amount: Decimal
    category: str
    source: str
    date: datetime
    notes: Optional[str] = None
    
    @field_validator('category')
    def validate_category(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError('Category cannot be empty')
        return v.strip()
    
    @field_validator('source')
    def validate_source(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError('Source cannot be empty')
        return v.strip()
    
    @field_validator('notes')
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() == "":
            raise ValueError('Notes cannot be empty string')
        return v.strip() if v else None


class IncomeCreate(IncomeBase):
    family_id: int


class IncomeUpdate(BaseModel):
    amount: Optional[Decimal] = None
    category: Optional[str] = None
    source: Optional[str] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None
    
    @field_validator('category')
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if v.strip() == "":
                raise ValueError('Category cannot be empty')
            return v.strip()
        return v
    
    @field_validator('source')
    def validate_source(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if v.strip() == "":
                raise ValueError('Source cannot be empty')
            return v.strip()
        return v
    
    @field_validator('notes')
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() == "":
            raise ValueError('Notes cannot be empty string')
        return v.strip() if v else None


class IncomeResponse(IncomeBase):
    id: int
    family_id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IncomeMonthlySummary(BaseModel):
    year: int
    month: int
    total_income: Decimal
    transaction_count: int
    by_category: Optional[dict] = {}
