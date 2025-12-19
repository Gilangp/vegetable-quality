from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, CurrentUserResponse, UserResponse, ProfileUpdateRequest
from app.controllers.auth import AuthController
from app.controllers.dependencies import get_current_user, get_optional_current_user
from config.database import get_db
from typing import Optional

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login dengan email dan password
    
    Returns access_token untuk digunakan di request berikutnya
    """
    controller = AuthController(db)
    return controller.login(credentials)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register user baru
    
    Username dan email harus unique
    """
    controller = AuthController(db)
    return controller.register(data)

@router.get("/me", response_model=CurrentUserResponse)
def get_me(current_user = Depends(get_current_user)):
    """
    Get current user profile
    
    Require authentication
    """
    return current_user

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Refresh access token
    
    Ambil token dari header Authorization: Bearer <token>
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    controller = AuthController(db)
    return controller.refresh_token(token)

@router.put("/profile", response_model=UserResponse)
def update_profile(
    data: ProfileUpdateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile
    
    Require authentication
    """
    controller = AuthController(db)
    return controller.update_profile(current_user, data)

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    
    Require authentication
    Body: 
    {
        "current_password": "string",
        "new_password": "string"
    }
    """
    controller = AuthController(db)
    return controller.change_password(current_user, data.current_password, data.new_password)

@router.post("/logout")
def logout(current_user = Depends(get_current_user)):
    """
    Logout (client-side JWT tidak perlu server logout)
    """
    return {
        "message": "Logout berhasil. Silakan hapus token dari client.",
        "user": current_user.username
    }
