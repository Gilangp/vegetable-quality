from app.models.residents import Residents
from app.models.families import Families
from app.models.houses import Houses
from app.schemas.residents import ResidentCreate, ResidentUpdate
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import random

class Resident:
    def __init__(self, db: Session):
        self.db = db

    def index(self, skip: int = 0, limit: int = 100):
        try:
            return self.db.query(Residents).offset(skip).limit(limit).all()
        except Exception as e:
            raise e

    def show(self, id: int):
        try:
            return self.db.query(Residents).filter(Residents.id == id).first()
        except Exception as e:
            raise e

    def store(self, data: ResidentCreate):
        try:
            resident_dict = data.model_dump()

            if not resident_dict.get('family_id') or resident_dict.get('family_id') == 0:
                available_families = self.db.query(Families.id).all()
                if available_families:
                    resident_dict['family_id'] = random.choice(available_families)[0]
                else:
                    resident_dict['family_id'] = 1

            if not resident_dict.get('house_id') or resident_dict.get('house_id') == 0:
                available_houses = self.db.query(Houses.id).all()
                if available_houses:
                    resident_dict['house_id'] = random.choice(available_houses)[0]
                else:
                    resident_dict['house_id'] = 1

            new_resident = Residents(**resident_dict)
            self.db.add(new_resident)
            self.db.commit()
            self.db.refresh(new_resident)
            return new_resident
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
        except Exception as e:
            raise e

    def update(self, id: int, data: ResidentUpdate):
        try:
            resident = self.db.query(Residents).filter(Residents.id == id).first()

            if not resident:
                return None

            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(resident, key, value)

            self.db.commit()
            self.db.refresh(resident)
            return resident
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
        except Exception as e:
            raise e

    def destroy(self, id: int):
        try:
            resident = self.db.query(Residents).filter(Residents.id == id).first()
            if resident:
                self.db.delete(resident)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
        except Exception as e:
            raise e