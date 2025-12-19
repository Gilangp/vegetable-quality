from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app.models.house import House as HouseModel
from app.models.resident_model import Resident as ResidentModel
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

            # Ensure residents are loaded so we can include them in response
            residents = house.residents or []
            house.resident_count = len(residents)

            # Build serializable dict matching HouseResponse, include residents list
            residents_list = []
            for r in residents:
                residents_list.append({
                    "id": r.id,
                    "family_id": r.family_id,
                    "house_id": r.house_id,
                    "nik": r.nik,
                    "name": r.name,
                    "gender": r.gender,
                    "birth_place": getattr(r, 'birth_place', None),
                    "birth_date": getattr(r, 'birth_date', None),
                    "phone": r.phone,
                    "religion": r.religion,
                    "blood_type": r.blood_type,
                    "education": r.education,
                    "occupation": r.occupation,
                    "status": r.status,
                    "created_at": r.created_at,
                    "updated_at": r.updated_at,
                })

            return {
                "id": house.id,
                "house_number": house.house_number,
                "address": house.address,
                "rt": house.rt,
                "rw": house.rw,
                "status": getattr(house, 'status', 'available'),
                "resident_count": house.resident_count,
                "residents": residents_list,
                "created_at": house.created_at,
                "updated_at": house.updated_at,
            }
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

    def assign_resident_to_house(self, house_id: int, resident_id: int):
        try:
            # Lock the target house row to avoid race conditions
            house = (
                self.db.query(HouseModel)
                .filter(HouseModel.id == house_id)
                .with_for_update()
                .first()
            )
            if not house:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="House not found")

            resident = (
                self.db.query(ResidentModel)
                .filter(ResidentModel.id == resident_id)
                .first()
            )
            if not resident:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")

            old_house_id = resident.house_id

            # Determine if assignment is allowed
            if house.status == 'available':
                # Assign and mark house occupied
                # Check previous house occupancy to possibly free it
                prev_count = 0
                if old_house_id and old_house_id != house.id:
                    prev_count = self.db.query(ResidentModel).filter(ResidentModel.house_id == old_house_id).count()

                resident.house_id = house.id
                house.status = 'occupied'

                # If previous house will become empty, mark it available
                if old_house_id and old_house_id != house.id and prev_count <= 1:
                    prev_house = (
                        self.db.query(HouseModel).filter(HouseModel.id == old_house_id).with_for_update().first()
                    )
                    if prev_house:
                        prev_house.status = 'available'

                self.db.commit()
                self.db.refresh(resident)
                return resident

            elif house.status == 'occupied':
                # Allow only if resident belongs to same family as existing occupants
                occupant_family_ids = set([r.family_id for r in house.residents if r.family_id is not None])
                if resident.family_id in occupant_family_ids:
                    prev_count = 0
                    if old_house_id and old_house_id != house.id:
                        prev_count = self.db.query(ResidentModel).filter(ResidentModel.house_id == old_house_id).count()

                    resident.house_id = house.id

                    if old_house_id and old_house_id != house.id and prev_count <= 1:
                        prev_house = (
                            self.db.query(HouseModel).filter(HouseModel.id == old_house_id).with_for_update().first()
                        )
                        if prev_house:
                            prev_house.status = 'available'

                    self.db.commit()
                    self.db.refresh(resident)
                    return resident
                else:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="House is occupied by another family")
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid house status")

        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise e
