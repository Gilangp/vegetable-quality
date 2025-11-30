from app.models.residents import Residents
from app.schemas.residents import ResidentCreate, ResidentUpdate
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

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
            new_resident = Residents(**data.model_dump())
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

            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():setattr(resident, key, value)

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