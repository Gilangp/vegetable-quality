from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app.models.house import House as HouseModel
from app.schemas.house import HouseCreate, HouseUpdate
from datetime import datetime


class HouseController:
    """Controller untuk House (rumah) management"""

    def __init__(self, db: Session):
        self.db = db

    def list_houses(self, skip: int = 0, limit: int = 100):
        try:
            houses = self.db.query(HouseModel).offset(skip).limit(limit).all()
            for h in houses:
                h.resident_count = len(h.residents) if h.residents else 0
            return houses
        except Exception as e:
            raise e

    def get_house(self, house_id: int):
        try:
            house = self.db.query(HouseModel).filter(HouseModel.id == house_id).first()
            if not house:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="House not found")
            house.resident_count = len(house.residents) if house.residents else 0
            return house
        except HTTPException:
            raise
        except Exception as e:
            raise e

    def create_house(self, data: HouseCreate):
        try:
            new_house = HouseModel(
                house_number=data.house_number,
                address=data.address,
                rt=data.rt,
                rw=data.rw,
            )
            self.db.add(new_house)
            self.db.commit()
            self.db.refresh(new_house)
            new_house.resident_count = 0
            return new_house
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise e

    def update_house(self, house_id: int, data: HouseUpdate):
        try:
            house = self.db.query(HouseModel).filter(HouseModel.id == house_id).first()
            if not house:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="House not found")

            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(house, key, value)

            house.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(house)
            house.resident_count = len(house.residents) if house.residents else 0
            return house
        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_house(self, house_id: int):
        try:
            house = self.db.query(HouseModel).filter(HouseModel.id == house_id).first()
            if not house:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="House not found")

            resident_count = len(house.residents) if house.residents else 0
            if resident_count > 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot delete house with {resident_count} residents")

            self.db.delete(house)
            self.db.commit()
            return {"message": "House deleted"}
        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise e
