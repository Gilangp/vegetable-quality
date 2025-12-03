from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.auth_service import AuthService
from config.database import get_db
from typing import Optional

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency untuk mendapatkan current user dari token
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak ditemukan",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Decode token
    payload = AuthService.decode_token(token)
    
    if not payload or not payload.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    
    # Get user dari database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User tidak ditemukan"
        )
    
    return user

async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency untuk mendapatkan current user (optional)
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = AuthService.decode_token(token)
    
    if not payload or not payload.get("user_id"):
        return None
    
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    
    return user

def require_role(*roles: str):
    """
    Dependency untuk validate role user
    Usage: Depends(require_role("admin", "ketua_rt"))
    """
    async def check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role tidak authorized. Memerlukan: {', '.join(roles)}"
            )
        return current_user
    
    return check_role
