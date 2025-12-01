from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from config.database import Base


class Income(Base):
    __tablename__ = "incomes"
    
    id = Column(Integer, primary_key=True, index=True)
    related_table = Column(String(100), nullable=True)
    related_id = Column(Integer, nullable=True)
    amount = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
