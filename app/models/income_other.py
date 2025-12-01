from sqlalchemy import Column, Integer, String, DateTime, Text, func
from sqlalchemy.orm import relationship
from config.database import Base


class IncomeOther(Base):
    __tablename__ = "income_other"
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text(), nullable=True)
    source = Column(String(100), nullable=True)
    amount = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
