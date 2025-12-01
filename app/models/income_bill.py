from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from config.database import Base


class IncomeBill(Base):
    __tablename__ = "income_bills"
    
    id = Column(Integer, primary_key=True, index=True)
    resident_id = Column(Integer, ForeignKey("residents.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("income_categories.id"), nullable=False)
    amount = Column(Integer, nullable=True)
    due_date = Column(String(50), nullable=True)
    status = Column(String(50), nullable=True, default="unpaid")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    resident = relationship("Resident", back_populates="bills")
    category = relationship("IncomeCategory", back_populates="bills")
