from sqlalchemy import Column, Integer, String, DateTime, Text, func
from sqlalchemy.orm import relationship
from config.database import Base


class Spending(Base):
    __tablename__ = "spendings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=True)
    amount = Column(Integer, nullable=True)
    description = Column(Text(), nullable=True)
    proof_image = Column(String(100), nullable=True)
    proof_file = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
