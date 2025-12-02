from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app.models.resident_approval import ResidentApproval
from app.models.resident_model import Resident
from app.models.family import Family
from app.models.user import User
from app.schemas.resident_approval import ResidentApprovalUpdate, ResidentApprovalResponse
from datetime import datetime


class ResidentApprovalController:
    """Controller untuk resident approval management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_approvals(self, status_filter: str = None, skip: int = 0, limit: int = 100):
        """
        List resident approvals
        - Filter by status (pending_approval, approved, rejected)
        - Ordered by newest first
        """
        try:
            query = self.db.query(ResidentApproval)
            
            if status_filter:
                query = query.filter(ResidentApproval.status == status_filter)
            
            return query.order_by(ResidentApproval.created_at.desc()).offset(skip).limit(limit).all()
        except Exception as e:
            raise e
    
    def get_approval(self, approval_id: int):
        """Get single approval by ID"""
        try:
            approval = self.db.query(ResidentApproval).filter(
                ResidentApproval.id == approval_id
            ).first()
            
            if not approval:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Approval record tidak ditemukan"
                )
            
            return approval
        except HTTPException:
            raise
        except Exception as e:
            raise e
    
    def approve_resident(self, approval_id: int, data: ResidentApprovalUpdate, current_user: User):
        """
        Approve resident registration
        - Check approval exists
        - Get resident data (sudah punya family_id dari registrasi)
        - If family_id provided: reassign ke family lain (jika RT ingin ubah)
        - If family_id not provided: gunakan family_id dari registrasi
        - Set resident as head_resident jika family belum punya head
        - Update resident: status = "aktif"
        - Update approval: status = "approved", approved_by
        """
        try:
            # 1. Get approval record
            approval = self.db.query(ResidentApproval).filter(
                ResidentApproval.id == approval_id
            ).first()
            
            if not approval:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Approval record tidak ditemukan"
                )
            
            if approval.status != "pending_approval":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Hanya approval pending_approval yang bisa di-proses. Status: {approval.status}"
                )
            
            # 2. Get resident
            resident = self.db.query(Resident).filter(
                Resident.id == approval.resident_id
            ).first()
            
            if not resident:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Resident data tidak ditemukan"
                )
            
            # 3. Determine family_id
            # Jika RT provide family_id: gunakan itu (reassign)
            # Jika tidak: gunakan family_id dari registrasi (sudah auto-assigned)
            if data.family_id:
                # Verify family exists dan reassign
                family = self.db.query(Family).filter(Family.id == data.family_id).first()
                if not family:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Family dengan ID {data.family_id} tidak ditemukan"
                    )
                resident.family_id = data.family_id
                family_id = data.family_id
            else:
                # Use family_id dari registrasi
                if not resident.family_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Resident tidak punya family_id. Silakan hubungi admin."
                    )
                family_id = resident.family_id
            
            # 4. Update resident status
            resident.status = "aktif"
            resident.updated_at = datetime.now()
            
            # 5. Set resident as head_resident if family doesn't have one
            family = self.db.query(Family).filter(Family.id == family_id).first()
            if family and not family.head_resident_id:
                family.head_resident_id = resident.id
            
            # 6. Update approval record
            approval.status = "approved"
            approval.approved_by = current_user.id
            approval.updated_at = datetime.now()
            
            # 7. Commit
            self.db.commit()
            self.db.refresh(approval)
            
            return approval
            
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
    
    def reject_resident(self, approval_id: int, data: ResidentApprovalUpdate, current_user: User):
        """
        Reject resident registration
        - Check approval exists
        - Update resident: status = "ditolak"
        - Update approval: status = "rejected", approved_by, note
        """
        try:
            # 1. Get approval record
            approval = self.db.query(ResidentApproval).filter(
                ResidentApproval.id == approval_id
            ).first()
            
            if not approval:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Approval record tidak ditemukan"
                )
            
            if approval.status != "pending_approval":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Hanya approval pending_approval yang bisa di-reject. Status: {approval.status}"
                )
            
            # 2. Update resident
            resident = self.db.query(Resident).filter(
                Resident.id == approval.resident_id
            ).first()
            
            if not resident:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Resident data tidak ditemukan"
                )
            
            resident.status = "ditolak"
            resident.updated_at = datetime.now()
            
            # 3. Update approval record
            approval.status = "rejected"
            approval.approved_by = current_user.id
            approval.note = data.note  # Note field is for rejection reason
            approval.updated_at = datetime.now()
            
            # 4. Commit
            self.db.commit()
            self.db.refresh(approval)
            
            return approval
            
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
