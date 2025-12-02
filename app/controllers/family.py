from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app.models.family import Family
from app.models.resident_model import Resident
from app.schemas.family import FamilyCreate, FamilyUpdate
from datetime import datetime


class FamilyController:
    """Controller untuk family management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_families(self, skip: int = 0, limit: int = 100):
        """List all families"""
        try:
            families = self.db.query(Family).offset(skip).limit(limit).all()
            
            # Add resident_count untuk response
            for family in families:
                family.resident_count = len(family.residents) if family.residents else 0
            
            return families
        except Exception as e:
            raise e
    
    def get_family(self, family_id: int):
        """Get single family by ID"""
        try:
            family = self.db.query(Family).filter(Family.id == family_id).first()
            
            if not family:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Keluarga tidak ditemukan"
                )
            
            return family
        except HTTPException:
            raise
        except Exception as e:
            raise e
    
    def create_family(self, data: FamilyCreate):
        """Create new family"""
        try:
            # Check if family_number already exists
            existing_family = self.db.query(Family).filter(
                Family.family_number == data.family_number
            ).first()
            
            if existing_family:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Nomor keluarga '{data.family_number}' sudah terdaftar"
                )
            
            # Create new family
            new_family = Family(
                family_number=data.family_number,
                head_resident_id=data.head_resident_id
            )
            
            self.db.add(new_family)
            self.db.commit()
            self.db.refresh(new_family)
            
            return new_family
        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database error: {str(e)}"
            )
        except Exception as e:
            self.db.rollback()
            raise e
    
    def update_family(self, family_id: int, data: FamilyUpdate):
        """Update family"""
        try:
            family = self.db.query(Family).filter(Family.id == family_id).first()
            
            if not family:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Keluarga tidak ditemukan"
                )
            
            # Check if new family_number already exists
            if data.family_number and data.family_number != family.family_number:
                existing_family = self.db.query(Family).filter(
                    Family.family_number == data.family_number
                ).first()
                
                if existing_family:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Nomor keluarga '{data.family_number}' sudah terdaftar"
                    )
            
            # Update fields
            if data.family_number:
                family.family_number = data.family_number
            if data.head_resident_id is not None:
                family.head_resident_id = data.head_resident_id
            
            family.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(family)
            
            return family
        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database error: {str(e)}"
            )
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_family(self, family_id: int):
        """Delete family (only if no residents)"""
        try:
            family = self.db.query(Family).filter(Family.id == family_id).first()
            
            if not family:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Keluarga tidak ditemukan"
                )
            
            # Check if family has residents
            resident_count = self.db.query(Resident).filter(
                Resident.family_id == family_id
            ).count()
            
            if resident_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tidak dapat menghapus keluarga. Masih ada {resident_count} anggota keluarga"
                )
            
            self.db.delete(family)
            self.db.commit()
            
            return {"message": "Keluarga berhasil dihapus"}
        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database error: {str(e)}"
            )
        except Exception as e:
            self.db.rollback()
            raise e
    
    def add_resident_to_family(self, family_id: int, resident_id: int):
        """Add resident to family"""
        try:
            # Check family exists
            family = self.db.query(Family).filter(Family.id == family_id).first()
            if not family:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Keluarga tidak ditemukan"
                )
            
            # Check resident exists
            resident = self.db.query(Resident).filter(Resident.id == resident_id).first()
            if not resident:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Anggota tidak ditemukan"
                )
            
            # Check if already in family
            if resident.family_id == family_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Anggota sudah terdaftar di keluarga ini"
                )
            
            # Add to family
            resident.family_id = family_id
            resident.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(resident)
            
            return resident
        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database error: {str(e)}"
            )
        except Exception as e:
            self.db.rollback()
            raise e
    
    def remove_resident_from_family(self, family_id: int, resident_id: int):
        """Remove resident from family"""
        try:
            # Check family exists
            family = self.db.query(Family).filter(Family.id == family_id).first()
            if not family:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Keluarga tidak ditemukan"
                )
            
            # Check resident exists and is in family
            resident = self.db.query(Resident).filter(
                Resident.id == resident_id,
                Resident.family_id == family_id
            ).first()
            
            if not resident:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Anggota tidak ditemukan di keluarga ini"
                )
            
            # Remove from family (set to NULL or default family?)
            # For now, we'll reject if it's the head of family
            if family.head_resident_id == resident_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tidak dapat menghapus kepala keluarga. Ubah kepala keluarga terlebih dahulu"
                )
            
            resident.family_id = None
            resident.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(resident)
            
            return {"message": f"Anggota {resident.name} berhasil dihapus dari keluarga"}
        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database error: {str(e)}"
            )
        except Exception as e:
            self.db.rollback()
            raise e
