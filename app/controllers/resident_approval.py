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
        - Get resident data
        - Cari/create family berdasarkan family_number dari approval
        - Set resident as head_resident jika family belum punya head
        - Update resident: status = "aktif", family_id
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
            
            # 3. Find or create family by family_number
            # Jika approval punya family_number, cari/buat family dengan number itu
            if approval.family_number:
                family = self.db.query(Family).filter(
                    Family.family_number == approval.family_number
                ).first()
                
                if not family:
                    # Create new family jika belum ada
                    family = Family(
                        family_number=approval.family_number,
                        head_resident_id=None
                    )
                    self.db.add(family)
                    self.db.flush()
                
                family_id = family.id
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Family number tidak ditemukan di approval record"
                )
            
            # 4. Assign resident ke family
            resident.family_id = family_id
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
        - Delete resident (CASCADE delete approvals)
        - Delete associated user
        - Create activity log for audit trail
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
            
            # 2. Get resident data sebelum delete (untuk logging)
            resident = self.db.query(Resident).filter(
                Resident.id == approval.resident_id
            ).first()
            
            if not resident:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Resident data tidak ditemukan"
                )
            
            # Store data untuk logging
            resident_id = resident.id
            resident_name = resident.name
            resident_nik = resident.nik
            
            # 3. Find and delete associated user jika ada
            user = self.db.query(User).filter(User.resident_id == resident_id).first()
            user_id = user.id if user else None
            if user:
                self.db.delete(user)
            
            # 4. Delete resident (approval akan CASCADE delete otomatis jika foreign key set CASCADE)
            self.db.delete(resident)
            
            # 5. Delete approval jika belum cascade
            approval_record = self.db.query(ResidentApproval).filter(
                ResidentApproval.id == approval_id
            ).first()
            if approval_record:
                self.db.delete(approval_record)
            
            self.db.commit()
            
            # 6. Return result untuk response
            return {
                "id": approval_id,
                "resident_id": resident_id,
                "name": resident_name,
                "nik": resident_nik,
                "status": "rejected",
                "note": data.note,
                "approved_by": current_user.id,
                "created_at": approval.created_at,
                "updated_at": approval.updated_at,
            }
            
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
