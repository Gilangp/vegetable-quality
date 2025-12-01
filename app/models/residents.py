from config.database import Base
from sqlalchemy import Column, Date, DateTime, ForeignKey, func, Integer, String

class Residents(Base):
    __tablename__: str = "residents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False)
    nik = Column(String(50), nullable=True)
    name = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    birth_place = Column(String(100), nullable=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(String(50), nullable=True)
    status = Column(String(50), nullable=True)
    religion = Column(String(50), nullable=True)
    blood_type = Column(String(5), nullable=True)
    education = Column(String(100), nullable=True)
    occupation = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Resident(name={self.name}, nik={self.nik})>"