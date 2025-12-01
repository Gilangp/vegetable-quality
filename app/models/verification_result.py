from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from config.database import Base


class VerificationResult(Base):
    __tablename__ = "verification_results"
    
    id = Column(Integer, primary_key=True, index=True)
    resident_id = Column(Integer, ForeignKey("residents.id"), nullable=False)
    vegetable_name = Column(String(100), nullable=True)
    image = Column(String(100), nullable=True)
    result = Column(String(255), nullable=True)
    is_valid_for_marketplace = Column(Boolean, nullable=True, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    resident = relationship("Resident", back_populates="verifications")
    products = relationship("MarketplaceProduct", back_populates="verification")
