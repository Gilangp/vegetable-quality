from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, CurrentUserResponse, UserResponse
from app.controllers.auth import AuthController
from app.controllers.dependencies import get_current_user, get_optional_current_user
from config.database import get_db
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login dengan username dan password
    
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

@router.post("/logout")
def logout(current_user = Depends(get_current_user)):
    """
    Logout (client-side JWT tidak perlu server logout)
    """
    return {
        "message": "Logout berhasil. Silakan hapus token dari client.",
        "user": current_user.username
    }
