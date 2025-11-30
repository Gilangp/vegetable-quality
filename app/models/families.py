from config.database import Base
from sqlalchemy import Column, DateTime, func, Integer

class Families(Base):
    __tablename__: str = 'families'

    id = Column(Integer, primary_key=True, autoincrement=True)
    family_number = Column(Integer, nullable=True)
    head_resident_id = Column(Integer, nullable=True, unique=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Family(family_number={self.family_number}, head_resident_id={self.head_resident_id})>"