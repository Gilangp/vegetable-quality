from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from config.database import Base


class MarketplaceOrder(Base):
    __tablename__ = "marketplace_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("residents.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("marketplace_products.id"), nullable=False)
    quantity = Column(Integer, nullable=True)
    total_price = Column(Integer, nullable=True)
    status = Column(String(50), nullable=True, default="pending")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    buyer = relationship("Resident", back_populates="orders_as_buyer", foreign_keys=[buyer_id])
    product = relationship("MarketplaceProduct", back_populates="orders")
