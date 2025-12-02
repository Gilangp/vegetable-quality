from sqlalchemy.orm import Session
from app.models.user import User
from app.models.resident_model import Resident
from app.models.resident_approval import ResidentApproval
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse, CurrentUserResponse
from app.services.auth_service import AuthService
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime, date

class AuthController:
    """Controller untuk authentication"""
    
    def __init__(self, db: Session):
        self.db = db
        self.auth_service = AuthService()
    
    def login(self, credentials: LoginRequest) -> TokenResponse:
        """
        Login user dengan email dan password
        - Check user exist
        - Check password correct
        - Jika warga (resident_id != NULL): 
          * Check resident.status = "aktif" (bukan pindah/meninggal)
          * Check resident_approvals.status = "approved" (sudah di-approve RT)
        - Jika admin/rt/rw/bendahara: bypass resident check
        - Generate JWT token
        """
        # 1. Cari user by email
        user = self.db.query(User).filter(User.email == credentials.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email atau password salah"
            )
        
        # 2. Verify password
        if not self.auth_service.verify_password(credentials.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email atau password salah"
            )
        
        # 3. Check resident status (hanya untuk warga)
        # Admin/RT/RW/Bendahara tidak punya resident_id, bypass check
        if user.resident_id is not None:
            resident = self.db.query(Resident).filter(Resident.id == user.resident_id).first()
            if not resident:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Resident data tidak ditemukan"
                )
            
            # Check resident.status = aktif (bukan pindah/meninggal)
            if resident.status != "aktif":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Warga tidak aktif. Status: {resident.status}."
                )
            
            # Check resident_approvals.status = approved
            approval = self.db.query(ResidentApproval).filter(
                ResidentApproval.resident_id == resident.id
            ).order_by(ResidentApproval.created_at.desc()).first()
            
            if not approval or approval.status != "approved":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Akun belum disetujui oleh RT. Silakan hubungi RT untuk approval."
                )
        
        # 4. Generate token
        token_data = self.auth_service.generate_token_for_user(
            user_id=user.id,
            username=user.username,
            role=user.role
        )
        
        return TokenResponse(
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user=UserResponse.model_validate(user)
        )
    
    def register(self, data: RegisterRequest) -> UserResponse:
        """
        Register user baru dengan data resident
        - Hanya untuk >= 17 tahun
        - Anak (< 17) REJECT
        - Check NIK unique
        - Create Resident (pending approval)
        - Create User (linked ke resident)
        - Create ResidentApproval record
        """
        # 1. Validasi umur (hanya >= 17 tahun)
        today = date.today()
        age = today.year - data.birth_date.year - ((today.month, today.day) < (data.birth_date.month, data.birth_date.day))
        
        if age < 17:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Anak-anak (< 17 tahun) tidak bisa self-register. Silakan hubungi Admin/RT untuk pendaftaran."
            )
        
        # 2. Check apakah NIK sudah ada
        existing_nik = self.db.query(Resident).filter(Resident.nik == data.nik).first()
        if existing_nik:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NIK sudah terdaftar"
            )
        
        # 3. Check apakah username sudah ada
        existing_user = self.db.query(User).filter(User.username == data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username sudah terdaftar"
            )
        
        # 4. Check apakah email sudah ada
        if data.email:
            existing_email = self.db.query(User).filter(User.email == data.email).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email sudah terdaftar"
                )
        
        # 5. Hash password
        hashed_password = self.auth_service.hash_password(data.password)
        
        try:
            # 6. Create Resident (status "aktif" untuk self-register)
            # Note: Untuk approval workflow, RT akan ubah status ke "pindah"/"meninggal" jika diperlukan
            new_resident = Resident(
                nik=data.nik,
                name=data.name,
                gender=data.gender,
                birth_place=data.birth_place,
                birth_date=data.birth_date,
                phone=data.phone,
                status="aktif",  # Default aktif untuk self-register
                family_id=1,  # Temporary, will be updated by RT/Admin
                house_id=1    # Temporary, will be updated by RT/Admin
            )
            self.db.add(new_resident)
            self.db.flush()  # Get resident.id without commit
            
            # 7. Create User (linked to resident)
            new_user = User(
                name=data.name,
                username=data.username,
                email=data.email,
                password=hashed_password,
                phone=data.phone,
                role="warga",  # Default role
                resident_id=new_resident.id
            )
            self.db.add(new_user)
            self.db.flush()
            
            # 8. Create ResidentApproval record (pending_approval)
            approval = ResidentApproval(
                resident_id=new_resident.id,
                name=new_resident.name,
                nik=new_resident.nik,
                gender=new_resident.gender,
                birth_place=new_resident.birth_place,
                birth_date=str(new_resident.birth_date),
                phone=new_resident.phone,
                address=None,  # Will be filled from family/house later
                status="pending_approval",
                note=None
            )
            self.db.add(approval)
            
            # Commit semua
            self.db.commit()
            self.db.refresh(new_user)
            
            return UserResponse.model_validate(new_user)
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal membuat akun: {str(e)}"
            )
    
    def get_current_user(self, token: str) -> Optional[CurrentUserResponse]:
        """
        Get current user dari token
        """
        # Decode token
        payload = self.auth_service.decode_token(token)
        
        if not payload or not payload.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token tidak valid",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("user_id")
        
        # Get user dari database
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User tidak ditemukan"
            )
        
        return CurrentUserResponse.model_validate(user)
    
    def refresh_token(self, token: str) -> TokenResponse:
        """
        Refresh token yang masih valid
        """
        payload = self.auth_service.decode_token(token)
        
        if not payload or not payload.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token tidak valid"
            )
        
        user_id = payload.get("user_id")
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User tidak ditemukan"
            )
        
        # Generate new token
        token_data = self.auth_service.generate_token_for_user(
            user_id=user.id,
            username=user.username,
            role=user.role
        )
        
        return TokenResponse(
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user=UserResponse.model_validate(user)
        )
