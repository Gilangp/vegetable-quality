from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime, date

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: 'UserResponse'

class UserResponse(BaseModel):
    id: int
    resident_id: Optional[int] = None
    name: str
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class RegisterRequest(BaseModel):
    name: str
    username: str
    email: str
    password: str
    password_confirm: str
    phone: Optional[str] = None
    nik: str  # Nomor Induk Kependudukan (16 digits)
    gender: str  # Laki-laki, Perempuan
    birth_date: date  # YYYY-MM-DD
    birth_place: Optional[str] = None
    
    @field_validator('nik')
    def validate_nik(cls, v: str) -> str:
        if len(v) != 16:
            raise ValueError('NIK harus 16 digit')
        if not v.isdigit():
            raise ValueError('NIK hanya boleh berisi angka')
        return v
    
    @field_validator('gender')
    def validate_gender(cls, v: str) -> str:
        valid_genders = ['Laki-laki', 'Perempuan']
        if v not in valid_genders:
            raise ValueError(f'Gender harus salah satu dari: {", ".join(valid_genders)}')
        return v
    
    @field_validator('birth_date')
    def validate_birth_date(cls, v: date) -> date:
        if v > datetime.now().date():
            raise ValueError('Tanggal lahir tidak boleh di masa depan')
        return v
    
    @field_validator('username')
    def validate_username(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.lower()
    
    @field_validator('password')
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @field_validator('password_confirm')
    def validate_password_confirm(cls, v: str, info) -> str:
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v

class CurrentUserResponse(BaseModel):
    id: int
    resident_id: Optional[int] = None
    name: str
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    resident: Optional[dict] = None
    
    class Config:
        from_attributes = True
