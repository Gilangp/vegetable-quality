from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from config.database import Base


class FamilyMutation(Base):
    __tablename__ = "family_mutations"
    
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    mutation_type = Column(String(100), nullable=True)
    description = Column(Text(), nullable=True)
    alamat_lama = Column(Text(), nullable=True)
    alamat_baru = Column(Text(), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    family = relationship("Family", back_populates="mutations")
