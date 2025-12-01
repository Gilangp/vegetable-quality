from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from config.database import Base


class MarketplaceProduct(Base):
    __tablename__ = "marketplace_products"
    
    id = Column(Integer, primary_key=True, index=True)
    resident_id = Column(Integer, ForeignKey("residents.id"), nullable=False)
    verification_id = Column(Integer, ForeignKey("verification_results.id"), nullable=True)
    name = Column(String(100), nullable=True)
    price = Column(Integer, nullable=True)
    stock = Column(Integer, nullable=True)
    description = Column(Text(), nullable=True)
    image = Column(String(100), nullable=True)
    status = Column(String(50), nullable=True, default="active")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    resident = relationship("Resident", back_populates="products")
    verification = relationship("VerificationResult", back_populates="products")
    orders = relationship("MarketplaceOrder", back_populates="product")
