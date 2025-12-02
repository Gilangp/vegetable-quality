from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from config.database import Base


class ResidentApproval(Base):
    __tablename__ = "resident_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    resident_id = Column(Integer, ForeignKey("residents.id"), nullable=True)
    name = Column(String(100), nullable=True)
    nik = Column(String(50), nullable=True)
    gender = Column(String(10), nullable=True)
    birth_place = Column(String(100), nullable=True)
    birth_date = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text(), nullable=True)
    status = Column(String(50), nullable=True, default="pending_approval")
    note = Column(Text(), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    resident = relationship("Resident", back_populates="approvals")
    approver = relationship("User", back_populates="approvals")
