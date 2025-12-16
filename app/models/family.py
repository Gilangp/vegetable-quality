from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from config.database import Base


class Family(Base):
    __tablename__ = "families"
    
    id = Column(Integer, primary_key=True, index=True)
    family_number = Column(String(50), nullable=True, unique=True)
    head_resident_id = Column(Integer, ForeignKey("residents.id"), nullable=True)
    ownership_status = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    residents = relationship("Resident", back_populates="family", foreign_keys="[Resident.family_id]")
    head_resident = relationship("Resident", foreign_keys=[head_resident_id], uselist=False)
    mutations = relationship("FamilyMutation", back_populates="family")
