from app.models.residents import Resident as ResidentSchema
from database.migrations.citizen import Citizen as CitizenDB
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

class Resident:
    def __init__(self, db: Session) -> None:
        self.db = db

    def store(self, data: ResidentSchema):
        try:
            new_resident = ResidentDB(**data.model_dump())
            self.db.add(new_resident)
            self.db.commit()
            self.db.refresh(new_citizen)
            return new_citizen
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
        except Exception as e:
            raise e

    def index(self):
        try:
            return self.db.query(CitizenDB).all()
        except Exception as e:
            raise e

    def update(self, nik: int, data: CitizenSchema):
        try:
            citizen = self.db.query(CitizenDB).filter_by(nik=nik).first()

            if not citizen:
                return None
            
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(citizen, key, value)
            
            self.db.commit()
            self.db.refresh(citizen)
            return citizen
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
        except Exception as e:
            raise e

    def destroy(self, nik: int):
        try:
            citizen = self.db.query(CitizenDB).filter_by(nik=nik).first()
            if citizen:
                self.db.delete(citizen)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
        except Exception as e:
            raise e