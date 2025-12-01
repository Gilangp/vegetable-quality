from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from config.database import Base


class Resident(Base):
    __tablename__ = "residents"
    
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False)
    nik = Column(String(50), nullable=True, unique=True, index=True)
    name = Column(String(100), nullable=True)
    gender = Column(String(50), nullable=True)
    birth_place = Column(String(100), nullable=True)
    birth_date = Column(Date(), nullable=True)
    phone = Column(String(50), nullable=True)
    religion = Column(String(50), nullable=True)
    blood_type = Column(String(10), nullable=True)
    education = Column(String(100), nullable=True)
    occupation = Column(String(100), nullable=True)
    status = Column(String(50), nullable=True, default="pending")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="resident", uselist=False)
    family = relationship("Family", back_populates="residents", foreign_keys=[family_id])
    house = relationship("House", back_populates="residents", foreign_keys=[house_id])
    messages = relationship("ResidentMessage", back_populates="resident")
    approvals = relationship("ResidentApproval", back_populates="resident")
    bills = relationship("IncomeBill", back_populates="resident")
    products = relationship("MarketplaceProduct", back_populates="resident")
    orders_as_buyer = relationship("MarketplaceOrder", back_populates="buyer", foreign_keys="[MarketplaceOrder.buyer_id]")
    verifications = relationship("VerificationResult", back_populates="resident")
