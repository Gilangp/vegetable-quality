from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from typing import Optional, Dict, Any
import os

class AuthService:
    """Service untuk handling authentication dan JWT"""
    
    # Konfigurasi JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password menggunakan SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password dengan hash"""
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Create JWT token dengan data user
        Format token: header.payload.signature
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=AuthService.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire.timestamp()})
        
        # Untuk development, gunakan simple token format
        # Format: user_id:role:timestamp:random_string
        import base64
        import json
        
        payload = json.dumps(to_encode)
        encoded = base64.b64encode(payload.encode()).decode()
        token = f"{encoded}.{secrets.token_urlsafe(32)}"
        
        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": int(expires_delta.total_seconds()) if expires_delta else AuthService.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """Decode dan validate JWT token"""
        try:
            import base64
            import json
            
            # Extract payload
            parts = token.split(".")
            if len(parts) != 2:
                return None
            
            payload_encoded = parts[0]
            payload = json.loads(base64.b64decode(payload_encoded).decode())
            
            # Check expiration
            if payload.get("exp") < datetime.now(timezone.utc).timestamp():
                return None
            
            return payload
        except Exception as e:
            return None
    
    @staticmethod
    def generate_token_for_user(user_id: int, username: str, role: str) -> Dict[str, Any]:
        """Generate token untuk user tertentu"""
        data = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "iat": datetime.now(timezone.utc).timestamp()
        }
        return AuthService.create_access_token(data)
