from sqlalchemy import Column, Integer, String, DateTime, Text, func
from sqlalchemy.orm import relationship
from config.database import Base


class IncomeCategory(Base):
    __tablename__ = "income_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    description = Column(Text(), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    bills = relationship("IncomeBill", back_populates="category")
