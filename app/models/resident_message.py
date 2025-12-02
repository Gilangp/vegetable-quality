from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from config.database import Base


class ResidentMessage(Base):
    __tablename__ = "resident_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    resident_id = Column(Integer, ForeignKey("residents.id"), nullable=False)
    subject = Column(String(100), nullable=True)
    message = Column(Text(), nullable=True)
    status = Column(String(50), nullable=True, default="pending")  # pending, read, resolved
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    resident = relationship("Resident", back_populates="messages")
