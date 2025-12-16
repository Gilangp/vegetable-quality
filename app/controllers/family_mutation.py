from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app.models.family_mutation import FamilyMutation
from app.models.family import Family
from app.schemas.family_mutation import FamilyMutationCreate
from datetime import datetime


class FamilyMutationController:
    def __init__(self, db: Session):
        self.db = db

    def list_mutations(self, skip: int = 0, limit: int = 100):
        try:
            return self.db.query(FamilyMutation).offset(skip).limit(limit).all()
        except Exception as e:
            raise e

    def get_mutation(self, mutation_id: int):
        try:
            m = self.db.query(FamilyMutation).filter(FamilyMutation.id == mutation_id).first()
            if not m:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mutasi tidak ditemukan")
            return m
        except HTTPException:
            raise
        except Exception as e:
            raise e

    def create_mutation(self, data: FamilyMutationCreate):
        try:
            # ensure family exists
            fam = self.db.query(Family).filter(Family.id == data.family_id).first()
            if not fam:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Keluarga tidak ditemukan")

            new = FamilyMutation(
                family_id=data.family_id,
                mutation_type=data.mutation_type,
                description=data.description,
                alamat_lama=getattr(data, 'alamat_lama', None),
                alamat_baru=getattr(data, 'alamat_baru', None),
            )
            self.db.add(new)
            self.db.commit()
            self.db.refresh(new)
            return new
        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_mutation(self, mutation_id: int):
        try:
            m = self.db.query(FamilyMutation).filter(FamilyMutation.id == mutation_id).first()
            if not m:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mutasi tidak ditemukan")
            self.db.delete(m)
            self.db.commit()
            return {"message": "Mutasi berhasil dihapus"}
        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise e
