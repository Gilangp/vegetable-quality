from config.database import Base
from sqlalchemy import Column, DateTime, func, Integer, String

class Houses(Base):
    __tablename__: str = "houses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    house_number = Column(String(50), nullable=True)
    address = Column(String(200), nullable=True)
    rt = Column(String(10), nullable=True)
    rw = Column(String(10), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<House(house_number={self.house_number}, address={self.address})>"