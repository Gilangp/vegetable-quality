from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from config.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    resident_id = Column(Integer, ForeignKey("residents.id"), nullable=True)
    name = Column(String(100), nullable=True)
    username = Column(String(50), nullable=True, unique=True, index=True)
    email = Column(String(100), nullable=True, unique=True, index=True)
    password = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    role = Column(String(50), nullable=True, default="warga")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    resident = relationship("Resident", back_populates="user", uselist=False)
    approvals = relationship("ResidentApproval", back_populates="approver")
    broadcasts = relationship("Broadcast", back_populates="sender")
