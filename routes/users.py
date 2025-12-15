from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from config.database import get_db
from app.models.user import User
from app.models.broadcast import Broadcast
from app.controllers.dependencies import get_current_user, require_role
from app.services.auth_service import AuthService

# Request/Response schemas
class UserCreateRequest(BaseModel):
    name: str
    email: str
    username: str
    password: str
    phone: Optional[str] = None
    role: str = "warga"  # Default role (sesuai BUSINESS_FLOW.md - 6 roles)

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    username: str
    phone: Optional[str]
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    id: int
    name: str
    email: str
    username: str
    phone: Optional[str]
    role: str
    
    class Config:
        from_attributes = True

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("", response_model=List[UserListResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all users (Admin only)
    
    Query params:
    - skip: Pagination offset (default: 0)
    - limit: Pagination limit (default: 100)
    - search: Search by name or email
    - role: Filter by role (admin, operator, viewer, etc)
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat melihat daftar pengguna"
        )
    
    query = db.query(User)
    
    # Apply search filter
    if search:
        search = search.lower()
        query = query.filter(
            (User.name.ilike(f"%{search}%")) | 
            (User.email.ilike(f"%{search}%")) |
            (User.username.ilike(f"%{search}%"))
        )
    
    # Apply role filter
    if role:
        query = query.filter(User.role == role)
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    
    return users

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user details (Admin only, or self)
    """
    # Check if user is admin or requesting own profile
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki akses ke data pengguna ini"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna tidak ditemukan"
        )
    
    return user

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new user (Admin only)
    
    Body:
    {
        "name": "string",
        "email": "string",
        "username": "string",
        "password": "string",
        "phone": "string (optional)",
        "role": "string (admin/operator/viewer)"
    }
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat membuat pengguna baru"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah terdaftar"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username sudah terdaftar"
        )
    
    # Hash password
    auth_service = AuthService()
    hashed_password = auth_service.hash_password(data.password)
    
    # Create new user
    new_user = User(
        name=data.name,
        email=data.email,
        username=data.username,
        password=hashed_password,
        phone=data.phone,
        role=data.role.lower()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user (Admin only)
    
    Body:
    {
        "name": "string (optional)",
        "email": "string (optional)",
        "phone": "string (optional)",
        "role": "string (optional)"
    }
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat mengubah data pengguna"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna tidak ditemukan"
        )
    
    # Check if new email is already taken by another user
    if data.email and data.email != user.email:
        existing_email = db.query(User).filter(
            User.email == data.email,
            User.id != user_id
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email sudah terdaftar"
            )
    
    # Update fields
    if data.name:
        user.name = data.name
    if data.email:
        user.email = data.email
    if data.phone is not None:
        user.phone = data.phone
    if data.role:
        user.role = data.role.lower()
    
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user (Admin only)
    
    Note: Cannot delete yourself
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat menghapus pengguna"
        )
    
    # Cannot delete yourself
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Anda tidak dapat menghapus akun sendiri"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna tidak ditemukan"
        )
    
    # Check if user has any broadcasts
    broadcast_count = db.query(Broadcast).filter(Broadcast.sent_by == user_id).count()
    if broadcast_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pengguna tidak dapat dihapus karena masih memiliki {broadcast_count} broadcast"
        )
    
    db.delete(user)
    db.commit()
    
    return None
