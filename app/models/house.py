from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from config.database import Base


class House(Base):
    __tablename__ = "houses"
    
    id = Column(Integer, primary_key=True, index=True)
    house_number = Column(String(50), nullable=True)
    address = Column(Text(), nullable=True)
    rt = Column(String(10), nullable=True)
    rw = Column(String(10), nullable=True)
    status = Column(String(20), nullable=False, server_default='available')
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    residents = relationship("Resident", back_populates="house", foreign_keys="[Resident.house_id]")
