from app.models.resident_model import Resident as ResidentModel
from app.models.family import Family
from app.models.house import House
from app.models.income_bill import IncomeBill
from app.models.marketplace_product import MarketplaceProduct
from app.models.marketplace_order import MarketplaceOrder
from app.models.resident_message import ResidentMessage
from app.models.resident_approval import ResidentApproval
from app.models.verification_result import VerificationResult
from app.schemas.residents import ResidentCreate, ResidentUpdate
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import random

class Resident:
    def __init__(self, db: Session):
        self.db = db

    def index(self, skip: int = 0, limit: int = 100):
        try:
            return self.db.query(ResidentModel).offset(skip).limit(limit).all()
        except Exception as e:
            raise e

    def show(self, id: int):
        try:
            return self.db.query(ResidentModel).filter(ResidentModel.id == id).first()
        except Exception as e:
            raise e

    def store(self, data: ResidentCreate):
        try:
            resident_dict = data.model_dump()

            if not resident_dict.get('family_id') or resident_dict.get('family_id') == 0:
                available_families = self.db.query(Family.id).all()
                if available_families:
                    resident_dict['family_id'] = random.choice(available_families)[0]
                else:
                    resident_dict['family_id'] = 1

            if not resident_dict.get('house_id') or resident_dict.get('house_id') == 0:
                available_houses = self.db.query(House.id).all()
                if available_houses:
                    resident_dict['house_id'] = random.choice(available_houses)[0]
                else:
                    resident_dict['house_id'] = 1

            new_resident = ResidentModel(**resident_dict)
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
            resident = self.db.query(ResidentModel).filter(ResidentModel.id == id).first()

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
            resident = self.db.query(ResidentModel).filter(ResidentModel.id == id).first()
            if resident:
                # Delete related records first to avoid foreign key constraint issues
                # Delete income bills
                self.db.query(IncomeBill).filter(IncomeBill.resident_id == id).delete()
                # Delete marketplace products
                self.db.query(MarketplaceProduct).filter(MarketplaceProduct.resident_id == id).delete()
                # Delete marketplace orders as buyer
                self.db.query(MarketplaceOrder).filter(MarketplaceOrder.buyer_id == id).delete()
                # Delete resident messages
                self.db.query(ResidentMessage).filter(ResidentMessage.resident_id == id).delete()
                # Delete resident approvals
                self.db.query(ResidentApproval).filter(ResidentApproval.resident_id == id).delete()
                # Delete verification results
                self.db.query(VerificationResult).filter(VerificationResult.resident_id == id).delete()
                # Finally delete the resident
                self.db.delete(resident)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
        except Exception as e:
            raise e